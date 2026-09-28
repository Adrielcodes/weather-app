import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

from weather import IMPERIAL, METRIC, WeatherError, current_summary, daily_forecast, fetch_forecast, hourly_frame, icon_url

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "london.json").read_text(encoding="utf-8"))


def mock_response(status, body):
    res = Mock(status_code=status)
    res.json.return_value = body
    return res


def test_current_summary_switches_units():
    c = current_summary(FIXTURE, METRIC)
    f = current_summary(FIXTURE, IMPERIAL)
    assert c["temp"] == round(FIXTURE["current"]["temp_c"])
    assert f["temp"] == round(FIXTURE["current"]["temp_f"])
    assert c["wind"] == round(FIXTURE["current"]["wind_kph"])
    assert f["wind"] == round(FIXTURE["current"]["wind_mph"])
    assert c["icon"].startswith("https://")


def test_hourly_frame_starts_at_current_hour():
    df = hourly_frame(FIXTURE, METRIC, hours=24)
    assert len(df) == 24
    local_hour = FIXTURE["location"]["localtime"][:13]
    assert df.index[0].strftime("%Y-%m-%d %H") == local_hour
    assert list(df.columns) == ["Temperature (°C)", "Chance of rain (%)"]


def test_daily_forecast_labels():
    days = daily_forecast(FIXTURE, IMPERIAL)
    assert len(days) == 3
    assert days[0]["label"] == "Today"
    assert all(d["high"] >= d["low"] for d in days)


def test_icon_url_handles_protocol_relative():
    assert icon_url({"icon": "//cdn.weatherapi.com/x.png"}) == "https://cdn.weatherapi.com/x.png"
    assert icon_url({}) == ""


@patch("weather.requests.get")
def test_fetch_success(get):
    get.return_value = mock_response(200, FIXTURE)
    assert fetch_forecast("London", "key") == FIXTURE
    assert get.call_args.kwargs["params"]["q"] == "London"


@patch("weather.requests.get")
def test_fetch_unknown_city(get):
    get.return_value = mock_response(400, {"error": {"code": 1006, "message": "No matching location found."}})
    with pytest.raises(WeatherError, match="No location found"):
        fetch_forecast("Nowhereville", "key")


@patch("weather.requests.get")
def test_fetch_bad_key(get):
    get.return_value = mock_response(401, {"error": {"code": 2006, "message": "API key is invalid."}})
    with pytest.raises(WeatherError, match="API key"):
        fetch_forecast("London", "bad")


@patch("weather.requests.get", side_effect=requests.ConnectionError)
def test_fetch_network_error(_get):
    with pytest.raises(WeatherError, match="connection"):
        fetch_forecast("London", "key")


def test_fetch_blank_city():
    with pytest.raises(WeatherError):
        fetch_forecast("   ", "key")
