
import json
from datetime import datetime, timezone

import pytest

import pipeline.analytics.run_logger as run_logger


def test_log_successful_pipeline_run(tmp_path, monkeypatch):
    log_file = tmp_path / "pipeline_runs.jsonl"
    monkeypatch.setattr(run_logger, "LOG_FILE", log_file)

    started_at = datetime.now(timezone.utc)

    output_path = run_logger.log_pipeline_run(
        pipeline_name="weather_silver",
        status="SUCCESS",
        records_processed=2,
        started_at=started_at,
    )

    assert output_path == log_file
    assert log_file.exists()

    record = json.loads(log_file.read_text(encoding="utf-8").strip())

    assert record["pipeline_name"] == "weather_silver"
    assert record["status"] == "SUCCESS"
    assert record["records_processed"] == 2
    assert record["duration_seconds"] >= 0
    assert record["error_message"] is None


def test_log_appends_multiple_runs(tmp_path, monkeypatch):
    log_file = tmp_path / "pipeline_runs.jsonl"
    monkeypatch.setattr(run_logger, "LOG_FILE", log_file)

    started_at = datetime.now(timezone.utc)

    for _ in range(2):
        run_logger.log_pipeline_run(
            pipeline_name="weather_ingestion",
            status="SUCCESS",
            records_processed=1,
            started_at=started_at,
        )

    lines = log_file.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2
    assert all(json.loads(line)["status"] == "SUCCESS" for line in lines)


def test_rejects_invalid_status(tmp_path, monkeypatch):
    monkeypatch.setattr(
        run_logger, "LOG_FILE", tmp_path / "pipeline_runs.jsonl"
    )

    with pytest.raises(ValueError, match="status"):
        run_logger.log_pipeline_run(
            pipeline_name="weather_silver",
            status="UNKNOWN",
            records_processed=1,
            started_at=datetime.now(timezone.utc),
        )


def test_rejects_naive_start_time(tmp_path, monkeypatch):
    monkeypatch.setattr(
        run_logger, "LOG_FILE", tmp_path / "pipeline_runs.jsonl"
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        run_logger.log_pipeline_run(
            pipeline_name="weather_silver",
            status="SUCCESS",
            records_processed=1,
            started_at=datetime.now(),
        )


def test_rejects_negative_record_count(tmp_path, monkeypatch):
    monkeypatch.setattr(
        run_logger, "LOG_FILE", tmp_path / "pipeline_runs.jsonl"
    )

    with pytest.raises(ValueError, match="records_processed"):
        run_logger.log_pipeline_run(
            pipeline_name="weather_silver",
            status="SUCCESS",
            records_processed=-1,
            started_at=datetime.now(timezone.utc),
        )
