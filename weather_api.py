"""
api/weather_api.py — Live weather using OpenWeatherMap API
Free tier: 60 calls/minute — more than enough for Aura
Get key at: https://openweathermap.org/api
"""

import requests
from utils.logger import get_logger
from config import USER_CITY

logger = get_logger(__name__)

# Switch to wttr.in which is 100% free and requires NO API KEY!
BASE_URL = "https://wttr.in"


class WeatherAPI:

    def get_weather(self, city: str = None) -> str:
        """
        Fetch current weather for a city and return a spoken response.
        If city is None, uses USER_CITY from config.
        """
        city = city or USER_CITY

        try:
            # format=j1 returns beautiful clean JSON data
            url = f"{BASE_URL}/{city}?format=j1"
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"Weather API error: {response.status_code}")
                return f"I couldn't get the weather for {city}. Please check the city name."

            data = response.json()
            return self._format_response(data, city)

        except requests.Timeout:
            return "Weather request timed out. Please check your internet connection."
        except Exception as e:
            logger.error(f"Weather fetch error: {e}")
            return "Something went wrong while fetching the weather."

    def _format_response(self, data: dict, city: str) -> str:
        """Convert raw wttr.in JSON data into a natural spoken sentence."""
        try:
            current = data["current_condition"][0]
            temp        = int(current["temp_C"])
            feels_like  = int(current["FeelsLikeC"])
            humidity    = current["humidity"]
            description = current["weatherDesc"][0]["value"]
            wind_speed  = current["windspeedKmph"]

            # Natural spoken response
            response = (
                f"Currently in {city}, it is {temp} degrees Celsius "
                f"with {description}. "
                f"It feels like {feels_like} degrees. "
                f"Humidity is {humidity} percent "
                f"and wind speed is {wind_speed} kilometres per hour."
            )

            # Add helpful tip based on weather
            if "rain" in description.lower() or "shower" in description.lower():
                response += " Don't forget to carry an umbrella!"
            elif temp >= 40:
                response += " It's very hot today. Stay hydrated!"
            elif temp <= 10:
                response += " It's quite cold. Please wear warm clothes!"

            return response

        except (KeyError, IndexError) as e:
            logger.error(f"Weather format error: {e}")
            return f"I got weather data for {city} but couldn't read it properly."

    def get_forecast(self, city: str = None) -> str:
        """Get 3-day forecast summary using wttr.in."""
        city = city or USER_CITY

        try:
            url = f"{BASE_URL}/{city}?format=j1"
            response = requests.get(url, timeout=5)
            data = response.json()

            if response.status_code != 200:
                return f"Could not get forecast for {city}."

            forecasts = data.get("weather", [])[:3]
            parts = []
            
            # Usually wttr gives 3 days of forecast in the 'weather' array
            for f in forecasts:
                desc = f["hourly"][4]["weatherDesc"][0]["value"] # Mid-day summary
                temp = f["maxtempC"]
                parts.append(f"{temp}°C with {desc}")

            return f"Forecast for {city}: " + ", then ".join(parts) + "."

        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return "Couldn't fetch the forecast right now."


# ── Singleton ─────────────────────────────────────────────
_api = None

def get_weather(city: str = None) -> str:
    global _api
    if _api is None:
        _api = WeatherAPI()
    return _api.get_weather(city)


# ── Quick test ────────────────────────────────────────────
if __name__ == "__main__":
    print(get_weather("Gwalior"))
    print(get_weather("Mumbai"))