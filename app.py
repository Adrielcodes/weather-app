"""Weather Explorer — Streamlit UI.

Run with:  streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st

from weather import IMPERIAL, METRIC, WeatherError, current_summary, daily_forecast, fetch_forecast, hourly_frame

st.set_page_config(page_title="Weather Explorer", page_icon="🌤️", layout="wide")


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets or an environment variable. Never hardcode it."""
    try:
        if "WEATHER_API_KEY" in st.secrets:
            return st.secrets["WEATHER_API_KEY"]
    except FileNotFoundError:
        pass  # no secrets.toml — fall back to the environment
    return os.environ.get("WEATHER_API_KEY")


@st.cache_data(ttl=600, show_spinner="Fetching the latest weather…")
def load_forecast(city: str, api_key: str) -> dict:
    # Cached for 10 minutes so switching units or re-running doesn't burn API calls
    return fetch_forecast(city, api_key)


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("🌤️ Weather Explorer")
    with st.form("search"):
        city = st.text_input("City", value=st.session_state.get("city", "London"), placeholder="e.g. Orlando, Tokyo, 10001")
        if st.form_submit_button("Search", use_container_width=True):
            st.session_state["city"] = city
    city = st.session_state.get("city", city)

    unit_choice = st.segmented_control("Units", ["°F", "°C"], default="°F", key="units")
    units = METRIC if unit_choice == "°C" else IMPERIAL

    st.caption("Data from [WeatherAPI.com](https://www.weatherapi.com/). Updates every 10 minutes.")

api_key = get_api_key()
if not api_key:
    st.error("No API key found.")
    st.info(
        "Get a free key at [weatherapi.com](https://www.weatherapi.com/signup.aspx), then either set the "
        "`WEATHER_API_KEY` environment variable or add it to `.streamlit/secrets.toml`:\n\n"
        '```toml\nWEATHER_API_KEY = "your-key-here"\n```'
    )
    st.stop()

try:
    data = load_forecast(city, api_key)
except WeatherError as err:
    st.warning(str(err))
    st.stop()

location = data["location"]
now = current_summary(data, units)

# ---------------------------------------------------------------- header
place = ", ".join(p for p in (location["name"], location["region"], location["country"]) if p)
st.title(place)
st.caption(f"Local time: {pd.to_datetime(location['localtime']).strftime('%A, %B %d · %I:%M %p')}")

hero_icon, hero_text = st.columns([1, 6], vertical_alignment="center")
hero_icon.image(now["icon"], width=96)
hero_text.markdown(
    f"<div style='font-size:3.5rem;font-weight:700;line-height:1'>{now['temp']}{units.temp_symbol}</div>"
    f"<div style='font-size:1.2rem'>{now['condition']} · H {now['high']}° / L {now['low']}°</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------- current conditions
st.subheader("Right now")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Feels like", f"{now['feels_like']}{units.temp_symbol}")
c2.metric("Humidity", f"{now['humidity']}%")
c3.metric("Wind", f"{now['wind']} {units.wind_label}", now["wind_dir"], delta_color="off")
c4.metric("UV index", now["uv"])
c5.metric("Chance of rain", f"{now['chance_of_rain']}%")
st.caption(f"🌅 Sunrise {now['sunrise']} · 🌇 Sunset {now['sunset']}")

# ---------------------------------------------------------------- hourly
st.subheader("Next 24 hours")
hourly = hourly_frame(data, units)
temp_tab, rain_tab = st.tabs(["Temperature", "Chance of rain"])
with temp_tab:
    st.line_chart(hourly[[f"Temperature ({units.temp_symbol})"]], color="#ff8a3d")
with rain_tab:
    st.bar_chart(hourly[["Chance of rain (%)"]], color="#3d8bff")

# ---------------------------------------------------------------- daily
forecast_days = daily_forecast(data, units)
st.subheader(f"{len(forecast_days)}-day forecast")
for col, day in zip(st.columns(len(forecast_days)), forecast_days):
    with col.container(border=True):
        st.markdown(f"**{day['label']}**  \n{day['date']}")
        st.image(day["icon"], width=56)
        st.markdown(f"**{day['high']}°** / {day['low']}°  \n{day['condition']}  \n💧 {day['chance_of_rain']}%")

# ---------------------------------------------------------------- map
st.subheader("Map")
st.map(pd.DataFrame({"lat": [location["lat"]], "lon": [location["lon"]]}), zoom=9)
