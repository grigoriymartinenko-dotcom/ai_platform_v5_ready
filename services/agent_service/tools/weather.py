# weather.py
# ------------------------
import httpx

from services.agent_service.tools.tool_registry import register_tool

API_KEY = "07108cf067a5fdf5aa26dce75354400f"


async def weather(city: str = ""):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            data = r.json()
        return {
            "success": True,
            "data": {
                "city": city,
                "temp": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"]
            },
            "error": None
        }
    except Exception as e:
        return {"success": False, "data": None, "error": str(e)}


register_tool(
    name="weather",
    description="Get weather for a city",
    schema={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    func=weather
)
