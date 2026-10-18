
import subprocess
import sys


STAGES = [
    ("Weather ingestion", "pipeline.ingestion.weather_ingest"),
    ("Silver transformation", "pipeline.transformation.weather_silver"),
    ("Parquet conversion", "pipeline.transformation.weather_parquet"),
]


def main() -> None:
    """Execute the weather pipeline stages sequentially."""
    for stage_name, module_name in STAGES:
        print(f"\n{'=' * 60}")
        print(f"Starting: {stage_name}")
        print("=" * 60, flush=True)

        result = subprocess.run(
            [sys.executable, "-m", module_name],
            check=False,
        )

        if result.returncode != 0:
            print(
                f"\nPipeline stopped: {stage_name} failed "
                f"with exit code {result.returncode}."
            )
            raise SystemExit(result.returncode)

        print(f"Completed: {stage_name}", flush=True)

    print("\nAll weather pipeline stages completed successfully.")


if __name__ == "__main__":
    main()
