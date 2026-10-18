
import pytest

from pipeline.transformation.weather_silver import transform_snapshot


def sample_weather():
    return {
        "latitude": 17.385,
        "longitude": 78.4867,
        "current": {
            "time": "2026-10-18T23:00",
            "temperature_2m": 26.7,
            "apparent_temperature": 30.2,
            "relative_humidity_2m": 71,
            "precipitation": 0.0,
            "wind_speed_10m": 6.2,
        },
    }


def test_transform_maps_weather_fields():
    record = transform_snapshot(
        sample_weather(),
        "2026-10-18T17:32:23+00:00",
    )

    assert record["observation_time"] == "2026-10-18T23:00"
    assert record["latitude"] == 17.385
    assert record["temperature_c"] == 26.7
    assert record["feels_like_c"] == 30.2
    assert record["humidity_pct"] == 71
    assert record["precipitation_mm"] == 0.0
    assert record["wind_speed_kmh"] == 6.2


def test_transform_preserves_ingestion_timestamp():
    ingested_at = "2026-10-18T17:32:23+00:00"

    record = transform_snapshot(sample_weather(), ingested_at)

    assert record["ingested_at_utc"] == ingested_at


def test_transform_rejects_missing_current_data():
    with pytest.raises(KeyError):
        transform_snapshot({"latitude": 17.385}, "2026-10-18T17:32:23+00:00")
