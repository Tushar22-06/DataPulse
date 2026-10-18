
import duckdb
from pathlib import Path


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
    output_path = convert_csv_to_parquet()
    print("Parquet conversion completed successfully.")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
