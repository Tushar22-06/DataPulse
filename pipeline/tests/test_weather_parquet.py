
from pathlib import Path

import duckdb

from pipeline.transformation.weather_parquet import convert_csv_to_parquet


def test_csv_to_parquet_conversion(tmp_path, monkeypatch):
    import pipeline.transformation.weather_parquet as weather_parquet

    csv_file = tmp_path / "weather_silver.csv"
    parquet_file = tmp_path / "weather_silver.parquet"

    csv_file.write_text(
        "observation_time,latitude,longitude,temperature_c,"
        "feels_like_c,humidity_pct,precipitation_mm,wind_speed_kmh,"
        "ingested_at_utc\n"
        "2026-10-18T23:00,17.385,78.4867,26.7,30.2,71,0.0,6.2,"
        "2026-10-18T17:32:23+00:00\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(weather_parquet, "SILVER_CSV", csv_file)
    monkeypatch.setattr(weather_parquet, "PARQUET_FILE", parquet_file)
    monkeypatch.setattr(weather_parquet, "PARQUET_DIR", tmp_path)

    output = convert_csv_to_parquet()

    assert output == parquet_file
    assert output.exists()

    with duckdb.connect() as con:
        row_count = con.execute(
            "SELECT COUNT(*) FROM read_parquet(?)",
            [str(output)],
        ).fetchone()[0]
        temperature = con.execute(
            "SELECT temperature_c FROM read_parquet(?)",
            [str(output)],
        ).fetchone()[0]

    assert row_count == 1
    assert temperature == 26.7
