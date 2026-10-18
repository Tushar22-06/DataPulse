
import duckdb


def test_weather_summary_metrics():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("""
            CREATE TABLE weather (
                temperature_c DOUBLE,
                humidity_pct DOUBLE,
                precipitation_mm DOUBLE
            )
        """)

        connection.execute("""
            INSERT INTO weather VALUES
            (26.7, 71, 0.0),
            (30.0, 65, 1.5)
        """)

        result = connection.execute("""
            SELECT
                COUNT(*) AS total_observations,
                ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
                ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
                ROUND(SUM(precipitation_mm), 2)
                    AS total_precipitation_mm
            FROM weather
        """).fetchone()

        assert result == (2, 28.35, 68.0, 1.5)
    finally:
        connection.close()


def test_weather_quality_checks():
    connection = duckdb.connect(":memory:")

    try:
        connection.execute("""
            CREATE TABLE weather (
                temperature_c DOUBLE,
                humidity_pct DOUBLE,
                precipitation_mm DOUBLE
            )
        """)

        connection.execute("""
            INSERT INTO weather VALUES
            (26.7, 71, 0.0),
            (NULL, 105, -1.0)
        """)

        result = connection.execute("""
            SELECT
                COUNT(*) FILTER (
                    WHERE temperature_c IS NULL
                ),
                COUNT(*) FILTER (
                    WHERE humidity_pct IS NULL
                ),
                COUNT(*) FILTER (
                    WHERE humidity_pct < 0 OR humidity_pct > 100
                ),
                COUNT(*) FILTER (
                    WHERE precipitation_mm < 0
                )
            FROM weather
        """).fetchone()

        assert result == (1, 0, 1, 1)
    finally:
        connection.close()
