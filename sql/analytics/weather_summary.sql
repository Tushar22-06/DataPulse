
-- DataPulse: Silver weather analytics

-- 1. Total number of weather observations
SELECT
    COUNT(*) AS total_observations
FROM read_parquet('data/processed/weather/weather_silver.parquet');


-- 2. Current dataset summary
SELECT
    ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
    ROUND(MIN(temperature_c), 2) AS min_temperature_c,
    ROUND(MAX(temperature_c), 2) AS max_temperature_c,
    ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
    ROUND(SUM(precipitation_mm), 2) AS total_precipitation_mm
FROM read_parquet('data/processed/weather/weather_silver.parquet');


-- 3. Observations by date
SELECT
    CAST(observation_time AS DATE) AS observation_date,
    COUNT(*) AS observation_count,
    ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
    ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct
FROM read_parquet('data/processed/weather/weather_silver.parquet')
GROUP BY observation_date
ORDER BY observation_date;


-- 4. Basic data-quality checks
SELECT
    COUNT(*) FILTER (WHERE temperature_c IS NULL) AS missing_temperature,
    COUNT(*) FILTER (WHERE humidity_pct IS NULL) AS missing_humidity,
    COUNT(*) FILTER (
        WHERE humidity_pct < 0 OR humidity_pct > 100
    ) AS invalid_humidity,
    COUNT(*) FILTER (
        WHERE precipitation_mm < 0
    ) AS negative_precipitation
FROM read_parquet('data/processed/weather/weather_silver.parquet');
