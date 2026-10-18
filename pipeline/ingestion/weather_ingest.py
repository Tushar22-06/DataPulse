
import json
from datetime import datetime, timezone
from pathlib import Path

import requests


API_URL = "https://api.open-meteo.com/v1/forecast"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "weather"

PARAMS = {
    "latitude": 17.3850,
    "longitude": 78.4867,
    "current": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "apparent_temperature,"
        "precipitation,"
        "wind_speed_10m"
    ),
    "timezone": "Asia/Kolkata",
}


def fetch_weather() -> dict:
    """Fetch current weather data for Hyderabad."""
    response = requests.get(API_URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    return response.json()


def save_raw_snapshot(data: dict) -> Path:
    """Save the original API response as a timestamped JSON file."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = RAW_DATA_DIR / f"weather_{timestamp}.json"

    with output_path.open("x", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return output_path


def main() -> None:
    weather_data = fetch_weather()
    output_path = save_raw_snapshot(weather_data)

    print(f"Weather data fetched successfully.")
    print(f"Raw snapshot saved to: {output_path}")
    print(json.dumps(weather_data["current"], indent=2))


if __name__ == "__main__":
    main()
