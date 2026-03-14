# services/agent_service/tools/plan.py
from services.utils.logger import get_logger, TraceAdapter
from services.agent_service.tools.tool_registry import register_tool

logger = TraceAdapter(get_logger("PlanTool"), {})


def plan_tool(args: dict):
    """
    Простой рабочий инструмент PLAN.
    Принимает 'task' и возвращает план действий.
    """
    task = args.get("task", "")
    logger.debug(f"[AGENT PLAN] {task}")

    plan_steps = [
        f"Шаг 1 для задачи: {task}",
        f"Шаг 2 для задачи: {task}",
        f"Шаг 3 для задачи: {task}"
    ]

    result_text = "\n".join(plan_steps)
    return {"result": result_text}


# Регистрация инструмента
register_tool("plan", "Generate plan for task", plan_tool)
