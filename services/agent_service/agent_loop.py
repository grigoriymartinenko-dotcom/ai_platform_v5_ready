# services/agent_service/agent_loop.py
import json
import re
import httpx
from sympy import sympify

from services.agent_service.parser import parse_llm_output
from services.agent_service.prompt import SYSTEM_PROMPT
from services.agent_service.tools.tool_registry import run_tool, list_tools, generate_tool_prompt
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("AgentLoop"), {})

LLM_URL = "http://localhost:8100/chat"


class AgentLoop:

    async def call_llm(self, messages):
        tool_prompt = generate_tool_prompt()
        prompt = SYSTEM_PROMPT + "\n\nTools:\n" + tool_prompt + "\n\nConversation:\n"

        for m in messages:
            prompt += f"{m['role']}: {m['content']}\n"

        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(LLM_URL, json={"message": prompt})
            if r.status_code != 200:
                return ""

            answer = r.json().get("answer", "").strip()

            if answer.startswith("```"):
                answer = re.sub(r"```.*?\n", "", answer)
                answer = answer.replace("```", "")

            return answer.strip()

    async def execute_step(self, step_text: str):
        logger.info(f"EXECUTE STEP: {step_text}")

        messages = [{"role": "user", "content": step_text}]
        tool_results = []

        llm_output = await self.call_llm(messages)

        actions = parse_llm_output(llm_output)

        for action in actions:

            if action["type"] == "tool":
                tool_name = action["tool"]
                args = action.get("args", {})

                logger.info(f"CALL TOOL {tool_name} {args}")

                try:
                    if tool_name == "calculator" and "expression" in args:
                        result = str(sympify(args["expression"]).evalf())
                    else:
                        result = await run_tool(tool_name, args)
                except Exception as e:
                    result = f"Tool error: {e}"

                tool_results.append(f"{tool_name}: {result}")

            elif action["type"] == "final":
                tool_results.append(action["content"])

        return "\n".join(tool_results)


agent_loop = AgentLoop()