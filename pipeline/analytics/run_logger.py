
import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = PROJECT_ROOT / "data" / "metadata" / "pipeline_runs.jsonl"


def log_pipeline_run(
    pipeline_name: str,
    status: str,
    records_processed: int,
    started_at: datetime,
    error_message: str | None = None,
) -> Path:
    """Append one pipeline-run record to a JSON Lines log."""
    if status not in {"SUCCESS", "FAILED"}:
        raise ValueError("status must be SUCCESS or FAILED")

    if records_processed < 0:
        raise ValueError("records_processed cannot be negative")

    finished_at = datetime.now(timezone.utc)
    if started_at.tzinfo is None or started_at.utcoffset() is None:
        raise ValueError("started_at must be timezone-aware")

    duration_seconds = (
        finished_at - started_at.astimezone(timezone.utc)
    ).total_seconds()

    run_record = {
        "pipeline_name": pipeline_name,
        "status": status,
        "records_processed": records_processed,
        "started_at_utc": started_at.astimezone(timezone.utc).isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": round(duration_seconds, 3),
        "error_message": error_message,
    }

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(run_record) + "\n")

    return LOG_FILE
