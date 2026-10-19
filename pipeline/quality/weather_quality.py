import math

REQUIRED_FIELDS = (
    "observation_time",
    "latitude",
    "longitude",
    "temperature_c",
    "feels_like_c",
    "humidity_pct",
    "precipitation_mm",
    "wind_speed_kmh",
    "ingested_at_utc",
)

NUMERIC_FIELDS = (
    "latitude",
    "longitude",
    "temperature_c",
    "feels_like_c",
    "humidity_pct",
    "precipitation_mm",
    "wind_speed_kmh",
)


def validate_silver_records(records: list[dict]) -> list[str]:
    """Return a list of data-quality issues found in Silver records."""
    issues = []
    seen_keys = set()

    for index, record in enumerate(records):
        prefix = f"Record {index + 1}"

        missing = [
            field
            for field in REQUIRED_FIELDS
            if field not in record or record[field] is None
        ]

        if missing:
            issues.append(f"{prefix}: missing fields {missing}")
            continue

        for field in ("observation_time", "ingested_at_utc"):
            if not isinstance(record[field], str) or not record[field].strip():
                issues.append(
                    f"{prefix}: {field} must be a non-empty string"
                )

        # IMPORTANT: initialize this OUTSIDE both loops above.
        invalid_numeric_fields = []

        for field in NUMERIC_FIELDS:
            value = record[field]

            if isinstance(value, bool) or not isinstance(value, (int, float)):
                issues.append(f"{prefix}: {field} must be numeric")
                invalid_numeric_fields.append(field)
            elif not math.isfinite(value):
                issues.append(f"{prefix}: {field} must be finite")
                invalid_numeric_fields.append(field)

        if invalid_numeric_fields:
            continue

        if not 0 <= record["humidity_pct"] <= 100:
            issues.append(
                f"{prefix}: humidity_pct must be between 0 and 100"
            )

        for field in ("precipitation_mm", "wind_speed_kmh"):
            if record[field] < 0:
                issues.append(f"{prefix}: {field} cannot be negative")

        key = (
            record["observation_time"],
            record["latitude"],
            record["longitude"],
        )

        if key in seen_keys:
            issues.append(f"{prefix}: duplicate observation key {key}")
        else:
            seen_keys.add(key)

    return issues

def build_quality_report(
    records: list[dict],
    issues: list[str],
) -> dict:
    """Build a summary report for Silver data-quality validation."""
    return {
        "records_checked": len(records),
        "issues_found": len(issues),
        "status": "PASSED" if not issues else "FAILED",
        "issues": issues,
    }