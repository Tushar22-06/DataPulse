
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "weather"
SILVER_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "weather"
OUTPUT_FILE = SILVER_DATA_DIR / "weather_silver.csv"

COLUMNS = [
    "observation_time",
    "latitude",
    "longitude",
    "temperature_c",
    "feels_like_c",
    "humidity_pct",
    "precipitation_mm",
    "wind_speed_kmh",
    "ingested_at_utc",
]


def transform_snapshot(data: dict, ingested_at: str) -> dict:
    """Transform a validated raw weather response into a Silver record."""
    current = data["current"]

    return {
        "observation_time": current["time"],
        "latitude": data["latitude"],
        "longitude": data["longitude"],
        "temperature_c": current["temperature_2m"],
        "feels_like_c": current["apparent_temperature"],
        "humidity_pct": current["relative_humidity_2m"],
        "precipitation_mm": current["precipitation"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "ingested_at_utc": ingested_at,
    }



def build_silver_records() -> list[dict]:
    """Read raw snapshots and deduplicate by observation time and location."""
    if not RAW_DATA_DIR.exists():
        raise FileNotFoundError(
            f"Raw weather directory not found: {RAW_DATA_DIR}"
        )

    records_by_key = {}

    for path in sorted(RAW_DATA_DIR.glob("*.json")):
        with path.open(encoding="utf-8") as file:
            data = json.load(file)

        ingested_at = datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=timezone.utc,
        ).isoformat()

        record = transform_snapshot(data, ingested_at)

        key = (
            record["observation_time"],
            record["latitude"],
            record["longitude"],
        )

        # Sorted filenames are processed in order, so the latest
        # filename wins if duplicate observation keys are encountered.
        records_by_key[key] = record

    return list(records_by_key.values())


def write_silver_csv(records: list[dict]) -> Path:
    """Write Silver records to a CSV file."""
    import csv

    SILVER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)

    return OUTPUT_FILE


def main() -> None:
    records = build_silver_records()
    output_path = write_silver_csv(records)

    print(f"Silver transformation completed: {len(records)} records")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
