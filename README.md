
# DataPulse — Real-Time Urban Intelligence Platform

DataPulse is a data engineering project that ingests public urban air-quality and weather data, transforms it into analytics-ready datasets, and exposes insights through APIs and dashboards.

## Project Goals

- Ingest real public air-quality and weather data.
- Build reliable, incremental data pipelines.
- Organize data into Bronze, Silver, and Gold layers.
- Validate data quality and track pipeline runs.
- Provide analytics through SQL and a web dashboard.
- Automate testing and ingestion workflows.

## Planned Technology Stack

- **Data engineering:** Python, SQL, Parquet, DuckDB
- **Backend:** Java 21, Spring Boot
- **Frontend:** Angular
- **Database:** PostgreSQL
- **Local infrastructure:** Docker Compose
- **Version control and CI:** Git and GitHub Actions

## Project Status

Initial repository setup. Features will be added incrementally and documented as they are implemented.

## Data Sources

- [OpenAQ](https://openaq.org/) — air-quality observations
- [Open-Meteo](https://open-meteo.com/) — weather data

## Development Principles

- Keep credentials and secrets out of source control.
- Prefer reproducible, tested, incremental pipelines.
- Document data quality checks and architectural decisions.
- Use real data and clearly label synthetic benchmark data.
