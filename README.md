# 🌤️ Weather Explorer

A Streamlit dashboard for current conditions and a 3-day forecast in any city in the world, powered by the [WeatherAPI.com](https://www.weatherapi.com/) API.

> One of my early Python projects from college, rebuilt in 2026. The original fetched current conditions only and had a few placeholder widgets. This version adds a real forecast, working unit switching, caching, error handling, and tests.

## Features

- **Search any location:** city name, ZIP/postcode, or coordinates
- **Current conditions at a glance:** temperature, feels-like, today's high/low, humidity, wind, UV index, chance of rain, sunrise and sunset
- **Next 24 hours:** interactive temperature and rain-chance charts starting from the location's local time
- **3-day forecast:** a card for each day with icons, highs/lows, and rain chance
- **°F / °C toggle:** switches every temperature and wind reading (mph ↔ km/h)
- **Map** of the location
- **Friendly errors** for unknown cities, bad API keys, and network problems
- **Cached requests:** results are reused for 10 minutes, so changing settings doesn't use up API calls

## Tech Stack

Python · Streamlit · pandas · requests · pytest

## Getting Started

**1. Get a free API key** from [weatherapi.com](https://www.weatherapi.com/signup.aspx).

**2. Install**

```bash
git clone https://github.com/Adrielcodes/weather-app.git
cd weather-app
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

**3. Add your key.** Either copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste your key in, or set an environment variable:

```bash
set WEATHER_API_KEY=your-key-here        # macOS/Linux: export WEATHER_API_KEY=your-key-here
```

`secrets.toml` is gitignored, so your key never ends up in the repo.

**4. Run**

```bash
streamlit run app.py
```

Then open http://localhost:8501.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests use a recorded API response (`tests/fixtures/london.json`), so they run offline. They cover the data helpers, API error handling, and a headless run of the full Streamlit app via `AppTest`.

## Project Structure

```
app.py        Streamlit UI (layout, charts, widgets)
weather.py    API client and data transforms, kept separate from the UI so they're easy to test
tests/        pytest suite + recorded API fixture
```

## Deploying

Deploys to [Streamlit Community Cloud](https://streamlit.io/cloud) for free. Point it at `app.py` and add `WEATHER_API_KEY` under **App settings → Secrets**.
