# services/agent_service/tools/weather.py

import httpx

from services.utils.logger import get_logger, TraceAdapter

logger = TraceAdapter(get_logger("WeatherTool"), {})

OPENWEATHER_API_KEY = "07108cf067a5fdf5aa26dce75354400f"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


async def weather(city: str):
    """
    Получение текущей погоды для указанного города через OpenWeather API.
    Возвращает строку с температурой, погодными условиями, ветром и влажностью.
    """
    if not city:
        return "Не указан город для прогноза погоды."

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(BASE_URL, params=params)
            data = response.json()
        except Exception as e:
            logger.debug(f"HTTP error: {e}")
            return f"Ошибка при запросе к OpenWeather API: {e}"

    if response.status_code != 200:
        message = data.get("message", "Неизвестная ошибка")
        return f"Ошибка OpenWeather API: {message}"

    # Парсим данные
    weather_desc = data["weather"][0]["description"].capitalize()
    temp = data["main"]["temp"]
    feels_like = data["main"]["feels_like"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    result = (
        f"Погода в {city}:\n"
        f"{weather_desc}\n"
        f"Температура: {temp}°C (ощущается как {feels_like}°C)\n"
        f"Влажность: {humidity}%\n"
        f"Ветер: {wind_speed} м/с"
    )

    return result
