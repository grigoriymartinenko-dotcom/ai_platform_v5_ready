# services/agent_service/agent_loop.py

import httpx
import json
from services.utils.logger import get_logger, TraceAdapter
from services.agent_service.tools.tool_registry import run_tool, list_tools
from services.agent_service.parser import parse_llm_output
from services.agent_service.prompt import SYSTEM_PROMPT
import asyncio

logger = TraceAdapter(get_logger("AgentLoop"), {})

LLM_URL = "http://localhost:8100/chat"
MAX_STEPS = 6


class AgentLoop:

    async def call_llm(self, messages):
        """
        Вызывает LLM с полным контекстом сообщений.
        """
        prompt = SYSTEM_PROMPT + "\n\n"
        for m in messages:
            prompt += f"{m['role']}: {m['content']}\n"

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                r = await client.post(LLM_URL, json={"message": prompt})
            except Exception as e:
                logger.debug(f"LLM HTTP error: {e}")
                return ""
            if r.status_code != 200:
                logger.debug(f"LLM ERROR {r.status_code}: {r.text}")
                return ""
            data = r.json()
            return data.get("answer", "")

    def fix_partial_json(self, text):
        """
        Попытка закрыть неполный JSON от LLM.
        """
        open_braces = text.count("{")
        close_braces = text.count("}")
        if open_braces > close_braces:
            text += "}" * (open_braces - close_braces)
        return text

    async def handle_message(self, user_message):
        """
        Основной цикл обработки сообщения:
        - Вызываем LLM
        - Выполняем инструменты
        - Добавляем результаты в контекст для следующего шага
        """
        logger.debug(f"STREAM USER MESSAGE: {user_message}")
        messages = [{"role": "user", "content": user_message}]

        # Лог доступных инструментов
        logger.debug(f"AVAILABLE TOOLS: {list(list_tools().keys())}")

        try:
            for step in range(MAX_STEPS):
                llm_output = await self.call_llm(messages)
                llm_output = self.fix_partial_json(llm_output)
                logger.debug(f"LLM STEP {step + 1}: {llm_output}")

                # Если LLM вернул пустоту
                if not llm_output.strip():
                    return f"USER: {user_message} AI: пустой ответ LLM", []

                try:
                    actions = parse_llm_output(llm_output)
                except Exception as e:
                    logger.debug(f"Parse LLM output error: {e}")
                    final_answer = f"USER: {user_message} AI: {llm_output.strip()}"
                    return final_answer, []

                if not actions:
                    final_answer = f"USER: {user_message} AI: {llm_output.strip()}"
                    return final_answer, []

                for action in actions:
                    if action["type"] == "tool":
                        tool_name = action["tool"]
                        args = action.get("args", {})

                        logger.debug(f"CALL TOOL {tool_name} {args}")
                        try:
                            result = await run_tool(tool_name, args)
                            logger.debug(f"TOOL RESULT {result}")

                            return str(result), []
                        except Exception as e:
                            result = f"Ошибка выполнения инструмента '{tool_name}': {e}"
                            logger.debug(result)

                        logger.debug(f"TOOL RESULT {result}")

                        # Добавляем результат инструмента в контекст LLM
                        messages.append({"role": "tool", "content": str(result)})

                    elif action["type"] == "final":
                        final_answer = f"AI: {action['content']}"
                        return final_answer, []

            # Если достигнут лимит шагов
            return f"USER: {user_message} AI: Не удалось завершить задачу", []

        except Exception as e:
            logger.debug(f"ERROR in AgentLoop: {e}")
            return f"USER: {user_message} AI: ошибка агента", []


agent_loop = AgentLoop()
