# services/agent_service/executor.py

from services.agent_service.tools.tool_registry import run_tool


async def execute_plan(plan):

    results = []

    for step in plan.get("steps", []):

        tool = step.get("tool")
        args = step.get("args", {})

        if not tool:
            results.append({"error": "No tool"})
            continue

        try:
            result = await run_tool(tool, args)
        except Exception as e:
            result = f"Tool error: {e}"

        results.append({
            "tool": tool,
            "args": args,
            "result": result
        })

    return results