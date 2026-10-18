
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PARQUET_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "weather"
    / "weather_silver.parquet"
)


def main() -> None:
    if not PARQUET_FILE.exists():
        raise FileNotFoundError(
            f"Parquet file not found: {PARQUET_FILE}. "
            "Run the ingestion and transformation steps first."
        )

    parquet_path = str(PARQUET_FILE).replace("'", "''")
    connection = duckdb.connect(":memory:")

    try:
        queries = {
            "Dataset summary": f"""
                SELECT
                    COUNT(*) AS total_observations,
                    ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
                    ROUND(MIN(temperature_c), 2) AS min_temperature_c,
                    ROUND(MAX(temperature_c), 2) AS max_temperature_c,
                    ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
                    ROUND(SUM(precipitation_mm), 2)
                        AS total_precipitation_mm
                FROM read_parquet('{parquet_path}')
            """,
            "Data-quality checks": f"""
                SELECT
                    COUNT(*) FILTER (
                        WHERE temperature_c IS NULL
                    ) AS missing_temperature,
                    COUNT(*) FILTER (
                        WHERE humidity_pct IS NULL
                    ) AS missing_humidity,
                    COUNT(*) FILTER (
                        WHERE humidity_pct < 0 OR humidity_pct > 100
                    ) AS invalid_humidity,
                    COUNT(*) FILTER (
                        WHERE precipitation_mm < 0
                    ) AS negative_precipitation
                FROM read_parquet('{parquet_path}')
            """,
        }

        for title, query in queries.items():
            print(f"\n--- {title} ---")
            result = connection.execute(query)
            print([column[0] for column in result.description])
            print(result.fetchall())

    finally:
        connection.close()


if __name__ == "__main__":
    main()
