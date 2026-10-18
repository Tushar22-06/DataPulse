
import json

from pipeline.ingestion.weather_ingest import save_raw_snapshot


def test_save_raw_snapshot(tmp_path, monkeypatch):
    sample_data = {
        "latitude": 17.385,
        "longitude": 78.4867,
        "current": {
            "time": "2026-10-18T23:00",
            "temperature_2m": 26.7,
            "relative_humidity_2m": 71,
        },
    }

    monkeypatch.setattr(
        "pipeline.ingestion.weather_ingest.RAW_DATA_DIR",
        tmp_path,
    )

    output_path = save_raw_snapshot(sample_data)

    assert output_path.exists()
    assert output_path.suffix == ".json"

    with output_path.open(encoding="utf-8") as file:
        saved_data = json.load(file)

    assert saved_data == sample_data


def test_weather_response_has_expected_fields():
    sample_response = {
        "current": {
            "time": "2026-10-18T23:00",
            "temperature_2m": 26.7,
            "relative_humidity_2m": 71,
            "apparent_temperature": 30.2,
            "precipitation": 0.0,
            "wind_speed_10m": 6.2,
        }
    }

    current = sample_response["current"]

    assert "time" in current
    assert "temperature_2m" in current
    assert "relative_humidity_2m" in current
