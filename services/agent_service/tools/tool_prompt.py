# services/agent_service/tools/tool_prompt.py

import json

from services.agent_service.tools.tool_registry import list_tools


def generate_tool_prompt(selected_tools=None):
    tools = list_tools()

    if selected_tools:
        tools = [t for t in tools if t["name"] in selected_tools]

    return f"""
You can use tools.

TOOLS:
{json.dumps(tools, indent=2, ensure_ascii=False)}

RULES:
- Always return valid JSON
- DO NOT write text outside JSON

Format:

Tool call:
{{
  "action": "tool_name",
  "args": {{
    ...
  }}
}}

Final answer:
{{
  "final": "your answer"
}}
"""
