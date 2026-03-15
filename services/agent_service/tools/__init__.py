# services/agent_service/tools/__init__.py

from .calculator import calculator
from .plan import plan_tool
from .read_page import read_page
from .think import think_tool
from .tool_registry import register_tool  # <-- важно использовать tool_registry
from .weather import weather
from .web_search import web_search

# регистрация инструментов через tool_registry
register_tool("web_search", "Search internet using Tavily", web_search)
register_tool("read_page", "Read webpage content", read_page)
register_tool("think", "Internal reasoning tool", think_tool)
register_tool("plan", "Create plan for a task", plan_tool)
register_tool("calculator", "Calculate math expression", calculator)
register_tool("weather", "Get weather for city", weather)
