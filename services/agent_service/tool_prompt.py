import json

from services.agent_service.tools.tool_registry import list_tools


def generate_tool_prompt():
    tools = list_tools()

    return f"""
You can use tools.

TOOLS:
{json.dumps(tools, indent=2)}

RULES:
- Always return JSON
- Use this format:

{{
  "action": "tool_name",
  "args": {{
    ...
  }}
}}

OR

{{
  "final": "your answer"
}}
"""