
import subprocess
import sys

import pipeline.run_pipeline as run_pipeline


def test_pipeline_runs_all_stages_in_order(monkeypatch):
    calls = []

    def fake_run(command, check):
        calls.append((command, check))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(run_pipeline.subprocess, "run", fake_run)

    run_pipeline.main()

    assert len(calls) == 3
    assert [call[0][-1] for call in calls] == [
        "pipeline.ingestion.weather_ingest",
        "pipeline.transformation.weather_silver",
        "pipeline.transformation.weather_parquet",
    ]
    assert all(check is False for _, check in calls)


def test_pipeline_stops_after_failed_stage(monkeypatch):
    calls = []

    def fake_run(command, check):
        calls.append(command)
        return_code = 1 if len(calls) == 2 else 0
        return subprocess.CompletedProcess(command, return_code)

    monkeypatch.setattr(run_pipeline.subprocess, "run", fake_run)

    try:
        run_pipeline.main()
        raise AssertionError("Expected SystemExit after stage failure")
    except SystemExit as error:
        assert error.code == 1

    assert len(calls) == 2
    assert calls[0][-1] == "pipeline.ingestion.weather_ingest"
    assert calls[1][-1] == "pipeline.transformation.weather_silver"
