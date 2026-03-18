from services.utils.logger import get_logger, TraceAdapter

base_logger = get_logger("ToolRegistry")
logger = TraceAdapter(base_logger, {})

TOOLS = {}


def register_tool(name, description, schema, func):
    if name in TOOLS:
        raise ValueError(f"Tool {name} already registered")

    TOOLS[name] = {
        "name": name,
        "description": description,
        "schema": schema,
        "func": func,
    }

    logger.info(f"REGISTER TOOL {name}")


def get_tool(name):
    return TOOLS.get(name)


def list_tools():
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "schema": tool["schema"],
        }
        for tool in TOOLS.values()
    ]


async def run_tool(name, args):
    tool = get_tool(name)

    if not tool:
        return {
            "success": False,
            "data": None,
            "error": f"Tool {name} not found"
        }

    try:
        result = await tool["func"](**args)

        if not isinstance(result, dict):
            return {
                "success": False,
                "data": None,
                "error": "Tool must return dict"
            }

        return result

    except Exception as e:
        logger.exception(f"Tool {name} failed")

        return {
            "success": False,
            "data": None,
            "error": str(e)
        }