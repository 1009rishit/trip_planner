import requests
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class OpenWeatherTool:
    """
    Tool to fetch daily weather forecast using OpenWeather 5-day / 3-hour forecast API.
    """

    def __init__(self):
        self.api_key = os.getenv("OPEN_WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OPEN_WEATHER_API_KEY not set in .env file")
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"

    def get_forecast(self, city: str, days: int = 5):
        """
        Fetch weather forecast for the given city, aggregated per day.

        Args:
            city (str): City name, e.g., "Paris,FR"
            days (int): Number of forecast days (max 5 for free API)

        Returns:
            list[dict]: Each dict contains date, min/max temp, and summary weather
        """
        if days > 5:
            days = 5  # Free API limit

        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }

        response = requests.get(self.base_url, params=params)
        if response.status_code != 200:
            raise Exception(f"OpenWeather API error: {response.status_code} - {response.text}")

        data = response.json()
        daily_data = defaultdict(list)

        # Group 3-hour forecasts by date
        for entry in data.get("list", []):
            date_str = datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d")
            if len(daily_data) < days:
                daily_data[date_str].append(entry)

        forecast_list = []
        for date, entries in daily_data.items():
            temps = [e["main"]["temp"] for e in entries]
            weather_descriptions = [e["weather"][0]["description"] for e in entries]
            # Choose the most frequent weather description
            weather_summary = max(set(weather_descriptions), key=weather_descriptions.count)
            forecast_list.append({
                "date": date,
                "temp_min": min(temps),
                "temp_max": max(temps),
                "weather": weather_summary
            })

        return forecast_list
