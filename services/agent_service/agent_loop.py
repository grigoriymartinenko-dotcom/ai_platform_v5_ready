# services/agent_service/agent_loop.py

import json
import re
import httpx
from sympy import sympify

from services.agent_service.parser import parse_llm_output
from services.agent_service.prompt import SYSTEM_PROMPT
from services.agent_service.tools.tool_registry import run_tool, generate_tool_prompt
from services.utils.logger import get_logger, TraceAdapter
from services.agent_service.tool_selector import tool_selector

logger = TraceAdapter(get_logger("AgentLoop"), {})

LLM_URL = "http://localhost:8100/chat"

MAX_RETRIES = 2
MAX_STEPS = 10

VALID_TOOLS = {"calculator", "web_search", "read_page", "weather"}


class ExecutionContext:
    def __init__(self, goal: str, plan=None):
        self.goal = goal
        self.plan = plan or []

        self.step_results = []
        self.intermediate_data = {}
        self.thoughts = []
        self.selected_tools = []

    def add_step(self, step, tool, args, result):
        self.step_results.append({
            "step": step,
            "tool": tool,
            "args": args,
            "result": result
        })

    def add_thought(self, thought):
        self.thoughts.append(thought)


class AgentLoop:

    def select_tools(self, context: ExecutionContext):
        try:
            query = context.goal

            if context.step_results:
                last = context.step_results[-1]
                query += f" {last['step']} {last['result']}"

            selected = tool_selector.select(query, top_k=3)

            if not selected:
                selected = ["web_search"]

            context.selected_tools = selected
            logger.info(f"SELECTED TOOLS: {selected}")

        except Exception as e:
            logger.error(f"Tool selection error: {e}")
            context.selected_tools = ["web_search"]

    async def call_llm(self, messages, context: ExecutionContext = None):

        if context:
            self.select_tools(context)
            tool_prompt = generate_tool_prompt(context.selected_tools)
        else:
            tool_prompt = generate_tool_prompt()

        prompt = SYSTEM_PROMPT + "\n\n"
        prompt += "Tools:\n" + tool_prompt + "\n\n"

        if context:
            prompt += f"GOAL:\n{context.goal}\n\n"

            if context.plan:
                prompt += f"PLAN:\n{json.dumps(context.plan, indent=2, ensure_ascii=False)}\n\n"

            if context.step_results:
                prompt += f"PREVIOUS STEPS:\n{json.dumps(context.step_results, indent=2, ensure_ascii=False)}\n\n"

            if context.intermediate_data:
                prompt += f"AVAILABLE DATA:\n{json.dumps(context.intermediate_data, indent=2, ensure_ascii=False)}\n\n"

            if context.selected_tools:
                prompt += f"AVAILABLE TOOLS NOW:\n{context.selected_tools}\n\n"

        prompt += "Conversation:\n"

        for m in messages:
            prompt += f"{m['role']}: {m['content']}\n"

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                r = await client.post(LLM_URL, json={"message": prompt})
            except Exception as e:
                logger.error(f"LLM HTTP error: {e}")
                return ""

            if r.status_code != 200:
                logger.error(f"LLM ERROR {r.status_code}: {r.text}")
                return ""

            answer = r.json().get("answer", "").strip()

            if answer.startswith("```"):
                answer = re.sub(r"```.*?\n", "", answer)
                answer = answer.replace("```", "")

            return answer.strip()

    # 🔥 FIX THINK
    async def think(self, context, step_text):
        messages = [{
            "role": "user",
            "content": f"""
Think step-by-step.

Step: {step_text}

Analyze:
- what we know
- what is missing
- next best action

НЕ используй JSON
НЕ вызывай инструменты
Пиши обычный текст
"""
        }]

        thought = await self.call_llm(messages, context)

        # 🔥 жёсткая очистка
        if any(x in thought for x in ["tool", "{", "}", "args", "final"]):
            thought = "Reasoning step"

        context.add_thought(thought)
        logger.info(f"THOUGHT: {thought}")

    async def act(self, context, step_text):
        messages = [{
            "role": "user",
            "content": f"""
Step: {step_text}

Верни ТОЛЬКО JSON:

- tool
или
- final

Не смешивай
"""
        }]

        output = await self.call_llm(messages, context)
        return parse_llm_output(output)

    async def execute(self, goal: str, plan: list):
        context = ExecutionContext(goal, plan)

        final_answer = None
        step_counter = 0

        for step_text in plan:

            if step_counter >= MAX_STEPS:
                logger.warning("MAX STEPS REACHED")
                break

            logger.info(f"\n===== STEP: {step_text} =====")

            await self.think(context, step_text)
            actions = await self.act(context, step_text)

            for action in actions:

                if action["type"] == "tool":

                    tool_name = action["tool"]
                    args = action.get("args", {})

                    if tool_name not in VALID_TOOLS:
                        continue

                    if context.selected_tools and tool_name not in context.selected_tools:
                        continue

                    # 🔥 запрет calculator вне math шага
                    if tool_name == "calculator" and "посчитать" not in step_text:
                        logger.warning("Calculator not allowed here")
                        continue

                    try:
                        if tool_name == "calculator":
                            result = str(sympify(args["expression"]).evalf())
                        else:
                            result = await run_tool(tool_name, args)

                    except Exception as e:
                        result = f"Tool error: {e}"

                    context.add_step(step_text, tool_name, args, result)
                    context.intermediate_data[tool_name] = result

                elif action["type"] == "final":
                    final_answer = action["content"]

            if final_answer:
                return final_answer

            step_counter += 1

        # 🔥 fallback
        if not context.intermediate_data:
            return "Не удалось получить данные"

        return str(context.intermediate_data)


agent_loop = AgentLoop()