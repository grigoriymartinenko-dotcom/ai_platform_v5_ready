# think.py
# ------------------------
from services.agent_service.tools.tool_registry import register_tool


async def think(thought: str = ""):
    return {"success": True, "data": {"thought": thought}, "error": None}


register_tool(
    name="think",
    description="Internal reasoning tool. Stores agent thoughts. Not for external use.",
    schema={"type": "object", "properties": {"thought": {"type": "string", "description": "Agent reasoning text"}},
            "required": ["thought"]},
    func=think
)
