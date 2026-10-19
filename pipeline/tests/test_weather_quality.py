import math

from pipeline.quality.weather_quality import validate_silver_records


def valid_record():
    return {
        "observation_time": "2026-10-19T00:00",
        "latitude": 17.385,
        "longitude": 78.4867,
        "temperature_c": 26.3,
        "feels_like_c": 30.0,
        "humidity_pct": 73,
        "precipitation_mm": 0.0,
        "wind_speed_kmh": 4.5,
        "ingested_at_utc": "2026-10-18T18:30:00+00:00",
    }


def test_valid_record_has_no_issues():
    assert validate_silver_records([valid_record()]) == []


def test_humidity_out_of_range_is_flagged():
    record = valid_record()
    record["humidity_pct"] = 120

    issues = validate_silver_records([record])

    assert any("humidity_pct" in issue for issue in issues)


def test_negative_precipitation_is_flagged():
    record = valid_record()
    record["precipitation_mm"] = -1

    issues = validate_silver_records([record])

    assert any("precipitation_mm" in issue for issue in issues)


def test_missing_field_is_flagged():
    record = valid_record()
    del record["temperature_c"]

    issues = validate_silver_records([record])

    assert any("temperature_c" in issue for issue in issues)


def test_duplicate_observations_are_flagged():
    record = valid_record()
    duplicate = valid_record()

    issues = validate_silver_records([record, duplicate])

    assert any("duplicate observation key" in issue for issue in issues)


def test_non_numeric_temperature_is_flagged():
    record = valid_record()
    record["temperature_c"] = "warm"

    issues = validate_silver_records([record])

    assert any("temperature_c must be numeric" in issue for issue in issues)


def test_nan_temperature_is_flagged():
    record = valid_record()
    record["temperature_c"] = math.nan

    issues = validate_silver_records([record])

    assert any("temperature_c must be finite" in issue for issue in issues)


def test_infinite_wind_speed_is_flagged():
    record = valid_record()
    record["wind_speed_kmh"] = math.inf

    issues = validate_silver_records([record])

    assert any("wind_speed_kmh must be finite" in issue for issue in issues)