
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import requests

from pipeline.analytics.run_logger import log_pipeline_run


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

REQUIRED_FIELDS = (
    "time",
    "temperature_2m",
    "relative_humidity_2m",
    "apparent_temperature",
    "precipitation",
    "wind_speed_10m",
)


def fetch_weather() -> dict:
    """Fetch current weather data for Hyderabad."""
    response = requests.get(API_URL, params=PARAMS, timeout=30)
    response.raise_for_status()
    return response.json()


def validate_weather(data: dict) -> None:
    """Raise ValueError if the API response fails basic quality checks."""
    if not isinstance(data, dict):
        raise ValueError("Response must be a JSON object.")

    current = data.get("current")
    if not isinstance(current, dict):
        raise ValueError("Missing or invalid 'current' object.")

    missing = [field for field in REQUIRED_FIELDS if field not in current]
    if missing:
        raise ValueError(f"Missing required weather fields: {missing}")

    if not isinstance(current["time"], str) or not current["time"].strip():
        raise ValueError("'time' must be a non-empty string.")

    for field in REQUIRED_FIELDS[1:]:
        value = current[field]
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"'{field}' must be a finite number.")

    if not 0 <= current["relative_humidity_2m"] <= 100:
        raise ValueError("Humidity must be between 0 and 100.")

    for field in ("precipitation", "wind_speed_10m"):
        if current[field] < 0:
            raise ValueError(f"'{field}' cannot be negative.")


def save_raw_snapshot(data: dict) -> Path:
    """Save the original API response as a timestamped JSON file."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = RAW_DATA_DIR / f"weather_{timestamp}.json"

    with output_path.open("x", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    return output_path


def main() -> None:
    started_at = datetime.now(timezone.utc)

    try:
        weather_data = fetch_weather()
        validate_weather(weather_data)
        output_path = save_raw_snapshot(weather_data)

        log_pipeline_run(
            pipeline_name="weather_ingestion",
            status="SUCCESS",
            records_processed=1,
            started_at=started_at,
        )

        print("Weather data fetched and validated successfully.")
        print(f"Raw snapshot saved to: {output_path}")
        print(json.dumps(weather_data["current"], indent=2))

    except Exception as error:
        try:
            log_pipeline_run(
                pipeline_name="weather_ingestion",
                status="FAILED",
                records_processed=0,
                started_at=started_at,
                error_message=f"{type(error).__name__}: {error}",
            )
        except Exception as logging_error:
            print(f"Warning: failed to write pipeline log: {logging_error}")

        raise


if __name__ == "__main__":
    main()
