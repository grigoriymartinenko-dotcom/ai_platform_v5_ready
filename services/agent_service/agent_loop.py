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
MAX_STEPS = 8

class AgentLoop:

    async def call_llm(self, messages):
        tool_prompt = generate_tool_prompt()
        prompt = SYSTEM_PROMPT + "\n\n" + tool_prompt + "\n\n"
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

    async def handle_message(self, user_message):
        logger.debug(f"STREAM USER MESSAGE: {user_message}")
        logger.debug(f"AVAILABLE TOOLS: {list_tools()}")

        messages = [{"role": "user", "content": user_message}]

        try:
            for step in range(MAX_STEPS):
                llm_output = await self.call_llm(messages)
                logger.debug(f"LLM STEP {step + 1}: {llm_output}")

                text = llm_output.strip()

                # tool(args) pattern
                tool_match = re.match(r"(\w+)\((.*?)\)", text)
                if tool_match:
                    tool_name = tool_match.group(1)
                    arg_text = tool_match.group(2)
                    try:
                        args = json.loads(arg_text)
                        if not isinstance(args, dict):
                            args = {"query": arg_text}
                    except:
                        args = {"query": arg_text}
                    llm_output = json.dumps({"tool": tool_name, "args": args})
                    logger.debug(f"Converted tool() → {llm_output}")

                # tool{json} pattern
                tool_json_match = re.match(r"(\w+)\s*(\{.*\})", text)
                if tool_json_match:
                    tool_name = tool_json_match.group(1)
                    json_part = tool_json_match.group(2)
                    try:
                        args = json.loads(json_part)
                    except:
                        args = {}
                    llm_output = json.dumps({"tool": tool_name, "args": args})
                    logger.debug(f"Converted tool{{}} → {llm_output}")

                actions = parse_llm_output(llm_output)

                for action in actions:
                    if action["type"] == "tool":
                        tool_name = action["tool"]
                        args = action.get("args", {})
                        logger.debug(f"CALL TOOL {tool_name} {args}")

                        try:
                            if tool_name == "calculator" and "expression" in args:
                                # sympy safe evaluation
                                expr = args["expression"]
                                try:
                                    result = sympify(expr).evalf()
                                except Exception as e:
                                    result = f"Calculation error: {e}"
                            else:
                                result = await run_tool(tool_name, args)
                        except Exception as e:
                            result = f"Tool error: {e}"

                        logger.debug(f"TOOL RESULT {result}")
                        messages.append({"role": "tool", "content": f"{tool_name} result:\n{result}"})

                    elif action["type"] == "final":
                        return action["content"], []

                if step == MAX_STEPS - 1:
                    return "Agent step limit reached", []

        except Exception as e:
            logger.debug(f"ERROR in AgentLoop: {e}")
            return "Agent error", []

agent_loop = AgentLoop()