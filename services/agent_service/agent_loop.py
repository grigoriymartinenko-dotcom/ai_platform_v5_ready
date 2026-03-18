# services/agent_service/agent_loop.py

import json
import re

import httpx

from services.agent_service.parser import parse_llm_output
from services.agent_service.prompt import SYSTEM_PROMPT
from services.agent_service.tool_selector import tool_selector
from services.agent_service.tools.tool_prompt import generate_tool_prompt
from services.agent_service.tools.tool_registry import run_tool
from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("AgentLoop"), {})

LLM_URL = "http://localhost:8100/chat"
MAX_RETRIES = 2
MAX_STEPS = 10
VALID_TOOLS = {"calculator", "web_search", "read_page", "weather", "think"}


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

    # -------------------------
    # TOOL SELECTION
    # -------------------------
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

    # -------------------------
    # FILTER TOOLS BY STEP
    # -------------------------
    def filter_tools_by_step(self, context: ExecutionContext, step_text: str):
        step_lower = step_text.lower()
        filtered = []

        for tool in context.selected_tools:
            if tool == "calculator":
                has_numbers = bool(re.search(r"\d", step_lower))
                has_math = any(x in step_lower for x in ["+", "-", "*", "/"])
                if not (has_numbers and has_math):
                    continue
            if tool == "weather":
                if "погод" not in step_lower and "температур" not in step_lower:
                    continue
            filtered.append(tool)

        if not filtered:
            filtered = context.selected_tools

        context.selected_tools = filtered
        logger.info(f"FILTERED TOOLS: {filtered}")

    # -------------------------
    # LLM CALL
    # -------------------------
    async def call_llm(self, messages, context: ExecutionContext = None):
        tool_prompt = generate_tool_prompt(context.selected_tools) if context else generate_tool_prompt()
        prompt = SYSTEM_PROMPT + "\n\nTOOLS:\n" + tool_prompt + "\n\n"

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

    # -------------------------
    # THINK
    # -------------------------
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
        if thought.strip().startswith("{") or len(thought.strip()) < 5:
            thought = "Reasoning step"
        context.add_thought(thought)
        logger.info(f"THOUGHT: {thought}")

    # -------------------------
    # ACT
    # -------------------------
    async def act(self, context, step_text):
        messages = [{
            "role": "user",
            "content": f"""
Step: {step_text}

Верни СТРОГО JSON:

1. Tool:
{{
  "action": "tool_name",
  "args": {{}}
}}

2. Final:
{{
  "final": "answer"
}}

Без текста вне JSON.
"""
        }]
        output = await self.call_llm(messages, context)
        if "{" in output:
            output = output[output.find("{"):]
        parsed = parse_llm_output(output)
        if isinstance(parsed, dict):
            parsed = [parsed]
        return parsed

    # -------------------------
    # MAIN EXECUTION
    # -------------------------
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
            self.select_tools(context)
            self.filter_tools_by_step(context, step_text)
            actions = await self.act(context, step_text)

            for action in actions:
                if "action" in action:
                    tool_name = action["action"]
                    args = action.get("args", {})

                    if tool_name == "calculator" and not re.search(r"\d", args.get("expression", "")):
                        logger.warning("BLOCKED EMPTY CALCULATION")
                        continue
                    if tool_name not in VALID_TOOLS:
                        logger.warning(f"INVALID TOOL: {tool_name}")
                        continue
                    if context.selected_tools and tool_name not in context.selected_tools:
                        logger.warning(f"TOOL NOT SELECTED: {tool_name}")
                        continue

                    logger.info(f"CALL TOOL: {tool_name} {args}")
                    result = await run_tool(tool_name, args)
                    context.add_step(step_text, tool_name, args, result)
                    context.intermediate_data[tool_name] = result.get("data") if result.get("success") else {
                        "error": result.get("error")}

                elif "final" in action:
                    final_answer = action["final"]

            if final_answer:
                return final_answer

            step_counter += 1

        if not context.intermediate_data:
            return "Не удалось получить данные"

        return json.dumps(context.intermediate_data, ensure_ascii=False, indent=2)


agent_loop = AgentLoop()