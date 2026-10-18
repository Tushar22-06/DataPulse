
import duckdb
from datetime import datetime, timezone
from pathlib import Path

from pipeline.analytics.run_logger import log_pipeline_run


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_CSV = PROJECT_ROOT / "data" / "processed" / "weather" / "weather_silver.csv"
PARQUET_DIR = PROJECT_ROOT / "data" / "processed" / "weather"
PARQUET_FILE = PARQUET_DIR / "weather_silver.parquet"


def convert_csv_to_parquet() -> Path:
    """Convert the Silver weather CSV into a Parquet file."""
    if not SILVER_CSV.exists():
        raise FileNotFoundError(
            f"Silver CSV not found: {SILVER_CSV}. "
            "Run weather_silver.py first."
        )

    PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(":memory:")
    try:
        csv_path = str(SILVER_CSV).replace("'", "''")
        parquet_path = str(PARQUET_FILE).replace("'", "''")

        connection.execute(
            f"""
            COPY (
                SELECT *
                FROM read_csv_auto('{csv_path}', header = true)
            )
            TO '{parquet_path}'
            (FORMAT PARQUET)
            """
        )
    finally:
        connection.close()

    return PARQUET_FILE


def main() -> None:
    started_at = datetime.now(timezone.utc)
    records_processed = 0

    try:
        output_path = convert_csv_to_parquet()

        # Count the rows actually written to the Parquet output.
        connection = duckdb.connect(":memory:")
        try:
            parquet_path = str(output_path).replace("'", "''")
            result = connection.execute(
                f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')"
            ).fetchone()
            records_processed = result[0]
        finally:
            connection.close()

        log_pipeline_run(
            pipeline_name="weather_parquet",
            status="SUCCESS",
            records_processed=records_processed,
            started_at=started_at,
        )

        print("Parquet conversion completed successfully.")
        print(f"Records processed: {records_processed}")
        print(f"Output saved to: {output_path}")

    except Exception as error:
        try:
            log_pipeline_run(
                pipeline_name="weather_parquet",
                status="FAILED",
                records_processed=records_processed,
                started_at=started_at,
                error_message=f"{type(error).__name__}: {error}",
            )
        except Exception as logging_error:
            print(f"Warning: failed to write pipeline log: {logging_error}")

        raise


if __name__ == "__main__":
    main()
