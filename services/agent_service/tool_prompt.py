from .tools.tool_registry import list_tools


def build_tool_prompt():
    tools = list_tools()

    prompt = "You can use tools.\n\n"

    for name, tool in tools.items():
        prompt += f"{name}: {tool['description']}\n"

    prompt += """

Use format:

THOUGHT: reasoning
ACTION: tool_name
INPUT: tool input

When done:

FINAL: answer
"""

    return prompt
