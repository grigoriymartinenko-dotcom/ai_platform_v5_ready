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
MAX_STEPS = 10


class AgentLoop:

    async def call_llm(self, messages):
        tool_prompt = generate_tool_prompt()
        prompt = SYSTEM_PROMPT + "\n\nAvailable tools:\n" + tool_prompt + "\n\nConversation:\n"

        for m in messages:
            role = m["role"]
            content = m["content"]
            prompt += f"{role}: {content}\n"

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                r = await client.post(LLM_URL, json={"message": prompt})
            except Exception as e:
                logger.error(f"LLM HTTP error: {e}")
                return ""

            if r.status_code != 200:
                logger.error(f"LLM ERROR {r.status_code}: {r.text}")
                return ""

            data = r.json()
            answer = data.get("answer", "")

            answer = answer.strip()
            if answer.startswith("```"):
                answer = re.sub(r"```.*?\n", "", answer)
                answer = answer.replace("```", "")

            return answer.strip()

    async def handle_message(self, user_message):
        logger.info(f"USER MESSAGE: {user_message}")
        logger.info(f"AVAILABLE TOOLS: {list_tools()}")

        messages = [{"role": "user", "content": user_message}]
        used_tools = set()

        for step in range(MAX_STEPS):
            llm_output = await self.call_llm(messages)

            if not llm_output:
                logger.warning("LLM returned empty output")
                return "LLM returned empty response", []

            logger.info(f"LLM STEP {step + 1}: {llm_output}")
            text = llm_output.strip()

            # support tool(args)
            tool_match = re.match(r"^(\w+)\((.*?)\)$", text)
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
                logger.info(f"Converted tool() → {llm_output}")

            # support tool{json}
            tool_json_match = re.match(r"^(\w+)\s*(\{.*\})$", text)
            if tool_json_match:
                tool_name = tool_json_match.group(1)
                json_part = tool_json_match.group(2)
                try:
                    args = json.loads(json_part)
                except:
                    args = {}
                llm_output = json.dumps({"tool": tool_name, "args": args})
                logger.info(f"Converted tool{{}} → {llm_output}")

            actions = parse_llm_output(llm_output)

            if not actions:
                logger.info("No structured output → treating as final")
                return llm_output, []

            final_answer = None
            tool_results_summary = []

            for action in actions:

                if action["type"] == "tool":
                    tool_name = action["tool"]
                    args = action.get("args", {})

                    if tool_name in used_tools and tool_name == "plan":
                        logger.warning("Prevented repeated planning")
                        continue

                    used_tools.add(tool_name)
                    logger.info(f"CALL TOOL {tool_name} {args}")

                    try:
                        if tool_name == "calculator" and "expression" in args:
                            expr = args["expression"]
                            try:
                                result = str(sympify(expr).evalf())
                            except Exception as e:
                                result = f"Calculation error: {e}"
                        else:
                            result = await run_tool(tool_name, args)

                        if tool_name == "web_search" and isinstance(result, str):
                            lines = []
                            for line in result.split("\n\n"):
                                match = re.match(r"(.+):\s*\((https?://.+)\)", line)
                                if match:
                                    title, url = match.groups()
                                    lines.append(f"[{title}]({url})")
                                else:
                                    lines.append(line)
                            result = "\n".join(lines)

                    except Exception as e:
                        result = f"Tool error: {e}"

                    logger.info(f"TOOL RESULT {result}")

                    if isinstance(result, (dict, list)):
                        result_text = json.dumps(result, ensure_ascii=False, indent=2)
                    else:
                        result_text = str(result)

                    tool_results_summary.append(f"{tool_name}: {result_text}")

                    messages.append({
                        "role": "tool",
                        "content": f"{tool_name} result:\n{result_text}"
                    })

                elif action["type"] == "final":
                    final_answer = action["content"]

            # 🔥 если есть final — возвращаем с результатами tools
            if final_answer:
                if tool_results_summary:
                    combined = "\n".join(tool_results_summary)
                    return f"{combined}\n\n{final_answer}", []
                return final_answer, []

        logger.warning("Agent step limit reached")
        return "Agent step limit reached", []


agent_loop = AgentLoop()