# services/agent_service/tools/calculator.py
from sympy import sympify

from services.agent_service.tools.tool_registry import register_tool


async def calculator(expression: str = ""):
    try:
        result = sympify(expression)
        return {"success": True, "data": {"result": float(result)}, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


register_tool(
    name="calculator",
    description="Evaluate mathematical expressions",
    schema={"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
    func=calculator
)
