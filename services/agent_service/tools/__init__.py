# services/agent_service/tools/__init__.py
from .router import register_tool
from .web_search import web_search
from .read_page import read_page

from services.agent_service.tools.think import think_tool
from services.agent_service.tools.plan import plan_tool

register_tool("web_search", "Search the internet", web_search)
register_tool("read_page", "Read webpage content", read_page)

register_tool("think", "Internal reasoning", think_tool)
register_tool("plan", "Create plan", plan_tool)
