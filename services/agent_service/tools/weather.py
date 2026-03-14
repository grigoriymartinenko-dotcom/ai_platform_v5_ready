# services/agent_service/tools/weather.py
from services.agent_service.tools.tool_registry import register_tool
from services.utils.logger import get_logger, TraceAdapter
import httpx

logger = TraceAdapter(get_logger("Weather"), {})
API_KEY = "07108cf067a5fdf5aa26dce75354400f"


async def weather(city: str = "") -> str:
    logger.info(f"WEATHER REQUEST {city}")
    if not city:
        return "Укажите город."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            data = r.json()
    except Exception as e:
        logger.debug(f"Weather HTTP error: {e}")
        return f"Не удалось получить погоду для {city}"

    if "main" not in data or "weather" not in data:
        logger.debug(f"WEATHER ERROR {data}")
        return f"Не удалось найти город: {city}"

    temp = data["main"]["temp"]
    description = data["weather"][0]["description"]
    return f"Погода в {city}: {temp}°C, {description}"


# регистрация через глобальный tool_registry
register_tool("weather", "Get weather for city", weather)
