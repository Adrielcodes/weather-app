"""Runs the real Streamlit script headlessly with the network mocked out."""

import json
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "london.json").read_text(encoding="utf-8"))
APP = str(Path(__file__).parent.parent / "app.py")


def test_app_renders_forecast(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    # app.py does `from weather import fetch_forecast` on each run, so patching the module is enough
    with patch("weather.fetch_forecast", return_value=FIXTURE):
        at = AppTest.from_file(APP, default_timeout=30)
        at.run()

    assert not at.exception
    assert "London" in at.title[0].value
    assert len(at.metric) == 5


def test_app_without_key_shows_setup_help(monkeypatch):
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()

    assert not at.exception
    assert at.error[0].value == "No API key found."
