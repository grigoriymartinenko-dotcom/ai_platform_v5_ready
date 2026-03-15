# services/agent_service/tools/__init__.py
from .tool_registry import register_tool
from .web_reader import read_page
from .web_search import web_search

# Регистрируем инструменты
register_tool(
    name="web_search",
    description="Search the web using Tavily API and return top results.",
    func=web_search
)

register_tool(
    name="read_page",
    description="Read webpage content and return top text up to limit.",
    func=read_page
)

from .calculator import calculator
from .plan import plan_tool

from .think import think_tool

from .weather import weather

# регистрация инструментов через tool_registry


register_tool("think", "Internal reasoning tool", think_tool)
register_tool("plan", "Create plan for a task", plan_tool)
register_tool("calculator", "Calculate math expression", calculator)
register_tool("weather", "Get weather for city", weather)
