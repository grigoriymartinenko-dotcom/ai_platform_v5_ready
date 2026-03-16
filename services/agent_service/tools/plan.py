from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("PlanTool"), {})


async def plan_tool(task: str = ""):
    """
    Инструмент планирования.
    Получает задачу и возвращает простой план действий.
    """

    logger.debug(f"[AGENT PLAN] {task}")

    if not task:
        return {"result": "No task provided"}

    steps = [
        f"1. Проанализировать задачу: {task}",
        f"2. Найти необходимую информацию",
        f"3. Сформировать ответ пользователю"
    ]

    result_text = "\n".join(steps)

    return {
        "result": result_text
    }


# регистрация инструмента
'''
register_tool(
    name="plan",
    description="Generate plan for a task",
    func=plan_tool
)
'''
