# services/agent_service/tools/calculator.py
# Правильно для всех инструментов
from services.agent_service.tools.tool_registry import register_tool


async def calculator(expr: str = "") -> str:
    try:
        result = eval(expr, {"__builtins__": {}})
        return f"{expr} = {result}"
    except Exception:
        return "Ошибка вычисления"


register_tool("calculator", "Calculate math expression", calculator)
