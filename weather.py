"""WeatherAPI.com client and data helpers.

Kept separate from the Streamlit UI so the logic can be unit tested
without a browser or network access.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd
import requests

API_URL = "https://api.weatherapi.com/v1/forecast.json"
FORECAST_DAYS = 3  # the free WeatherAPI plan includes a 3-day forecast


class WeatherError(Exception):
    """Raised with a user-friendly message when weather data can't be loaded."""


@dataclass(frozen=True)
class Units:
    temp: str  # "c" or "f"
    wind: str  # "kph" or "mph"
    temp_symbol: str
    wind_label: str


METRIC = Units(temp="c", wind="kph", temp_symbol="°C", wind_label="km/h")
IMPERIAL = Units(temp="f", wind="mph", temp_symbol="°F", wind_label="mph")


def fetch_forecast(city: str, api_key: str, days: int = FORECAST_DAYS) -> dict:
    """Fetch current conditions plus a multi-day forecast for a city."""
    if not city.strip():
        raise WeatherError("Enter a city name to get started.")
    try:
        response = requests.get(
            API_URL,
            params={"key": api_key, "q": city, "days": days, "aqi": "no", "alerts": "no"},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise WeatherError("Couldn't reach the weather service. Check your connection.") from exc

    if response.status_code == 200:
        return response.json()

    # WeatherAPI returns {"error": {"code": ..., "message": ...}} on failures
    try:
        error = response.json().get("error", {})
    except ValueError:
        error = {}
    if error.get("code") == 1006:
        raise WeatherError(f"No location found matching “{city}”. Try another spelling.")
    if response.status_code in (401, 403):
        raise WeatherError("The API key was rejected. Check WEATHER_API_KEY.")
    raise WeatherError(error.get("message") or f"Weather service error ({response.status_code}).")


def icon_url(condition: dict) -> str:
    """WeatherAPI icon URLs are protocol-relative (//cdn...)."""
    url = condition.get("icon", "")
    return f"https:{url}" if url.startswith("//") else url


def current_summary(data: dict, units: Units) -> dict:
    """Flatten current conditions into display-ready values."""
    cur = data["current"]
    today = data["forecast"]["forecastday"][0]
    return {
        "temp": round(cur[f"temp_{units.temp}"]),
        "feels_like": round(cur[f"feelslike_{units.temp}"]),
        "high": round(today["day"][f"maxtemp_{units.temp}"]),
        "low": round(today["day"][f"mintemp_{units.temp}"]),
        "condition": cur["condition"]["text"],
        "icon": icon_url(cur["condition"]),
        "humidity": cur["humidity"],
        "wind": round(cur[f"wind_{units.wind}"]),
        "wind_dir": cur["wind_dir"],
        "uv": cur["uv"],
        "chance_of_rain": today["day"]["daily_chance_of_rain"],
        "sunrise": today["astro"]["sunrise"],
        "sunset": today["astro"]["sunset"],
    }


def hourly_frame(data: dict, units: Units, hours: int = 24) -> pd.DataFrame:
    """The next `hours` hours starting from the location's current local hour."""
    local_now = datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M")
    current_hour = local_now.replace(minute=0)

    rows = [
        {
            "time": datetime.strptime(hour["time"], "%Y-%m-%d %H:%M"),
            f"Temperature ({units.temp_symbol})": hour[f"temp_{units.temp}"],
            "Chance of rain (%)": hour["chance_of_rain"],
        }
        for day in data["forecast"]["forecastday"]
        for hour in day["hour"]
    ]
    df = pd.DataFrame(rows)
    df = df[df["time"] >= current_hour].head(hours)
    return df.set_index("time")


def daily_forecast(data: dict, units: Units) -> list[dict]:
    """One entry per forecast day."""
    days = []
    for fd in data["forecast"]["forecastday"]:
        date = datetime.strptime(fd["date"], "%Y-%m-%d")
        day = fd["day"]
        days.append(
            {
                "label": date.strftime("%A"),
                "date": date.strftime("%b %d"),
                "high": round(day[f"maxtemp_{units.temp}"]),
                "low": round(day[f"mintemp_{units.temp}"]),
                "condition": day["condition"]["text"],
                "icon": icon_url(day["condition"]),
                "chance_of_rain": day["daily_chance_of_rain"],
            }
        )
    if days:
        days[0]["label"] = "Today"
    return days
