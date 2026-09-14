# GitHub Data Platform

A Dockerized data platform for collecting, transforming, and visualizing GitHub engineering data through a **Medallion Architecture**:

**Bronze → Silver → Gold → API → Dashboard**

The platform extracts real data from GitHub, processes it through a Prefect-managed pipeline, exposes analytical metrics through a FastAPI API, and displays them in a React/Vite dashboard.

---

## Architecture

```text
                         GitHub API
                             │
                             ▼
                    ┌─────────────────┐
                    │     BRONZE      │
                    │ Raw GitHub data │
                    │     JSON        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     SILVER      │
                    │ Cleaned /       │
                    │ normalized data │
                    │    Parquet      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      GOLD       │
                    │ Aggregated      │
                    │ engineering     │
                    │    metrics      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     FastAPI     │
                    │      REST       │
                    │      API        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ React / Vite    │
                    │   Dashboard     │
                    └─────────────────┘

                    Prefect
                       │
             orchestrates the pipeline
```

---

## Main Components

### Data ingestion

The Bronze layer retrieves data from GitHub using the GitHub API.

Currently collected data includes:

* repositories
* commits
* pull requests
* pull request commits
* GitHub Actions workflow runs

Raw data is stored as JSON under:

```text
storage/bronze/
```

---

### Silver layer

The Silver layer transforms raw GitHub data into normalized analytical datasets.

Current datasets include:

```text
storage/silver/
├── commits.parquet
├── repository_snapshots.parquet
├── pull_request_events.parquet
├── deploy_events.parquet
└── lead_times.parquet
```

Some datasets may not be generated when the source GitHub data contains no corresponding events.

For example:

* no pull requests → no lead-time data
* no successful workflow runs → no deployment events

The pipeline does not generate fake data to fill these gaps.

---

### Gold layer

The Gold layer contains aggregated datasets optimized for analytics and dashboard consumption.

Examples:

```text
storage/gold/
├── contributor_activity_weekly.parquet
├── contributor_activity_monthly.parquet
├── deploy_frequency_weekly.parquet
├── deploy_frequency_monthly.parquet
├── lead_time_weekly.parquet
└── lead_time_monthly.parquet
```

These datasets are produced from the Silver layer.

---

## Pipeline

The complete pipeline is orchestrated with **Prefect**.

The main flow is:

```text
run_pipeline_flow
        │
        ├── extract_bronze_flow
        │
        ├── build_silver_flow
        │
        └── build_gold_flow
```

### Bronze

```text
GitHub API
    ↓
repositories
commits
pull requests
PR commits
workflow runs
```

### Silver

```text
Bronze JSON
    ↓
normalized Parquet datasets
```

### Gold

```text
Silver Parquet
    ↓
aggregated engineering metrics
```

---

## Prefect

Prefect is used to orchestrate the pipeline and execute it through a worker.

The project uses:

* Prefect Server
* Prefect Worker
* Work Pool: `default-pool`

The deployment is defined in:

```text
prefect.yaml
```

Main deployment:

```text
run-full-pipeline/run-full-pipeline
```

---

## API

The backend is implemented with **FastAPI**.

The API reads data directly from the Gold/Silver/Bronze layers and exposes metrics to the dashboard.

Base URL:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

### Main endpoints

#### Summary

```http
GET /metrics/summary
```

Returns high-level metrics such as:

* total commits
* active contributors
* open pull requests
* average commits per week

#### Contributor activity

```http
GET /metrics/contributor-activity
```

Supports:

```text
?granularity=weekly
?granularity=monthly
```

#### Contributors

```http
GET /metrics/contributors
```

Returns contributor-level commit statistics.

#### Pull requests

```http
GET /metrics/pull-requests
```

Returns pull-request status information.

#### Deployment frequency

```http
GET /metrics/deploy-frequency
```

Supports weekly and monthly aggregation.

#### Lead time

```http
GET /metrics/lead-time
```

Supports weekly and monthly aggregation.

#### Activity trend

```http
GET /metrics/activity-trend
```

Supports:

```text
?granularity=weekly
?granularity=monthly
```

#### Repositories

```http
GET /metrics/repositories
```

Returns repository-level metrics including:

* commits
* primary language
* stars
* forks
* open issues
* visibility
* last push timestamp

---

## Dashboard

The frontend is built with:

* React
* Vite
* Recharts
* Axios

The dashboard consumes the FastAPI endpoints and displays the current data produced by the pipeline.

Dashboard URL:

```text
http://localhost:5173
```

The dashboard currently includes:

* summary cards
* activity trend
* contributor statistics
* pull-request status
* repository metrics

The dashboard is designed to display empty states when the underlying dataset does not contain data rather than displaying mock values.

---

## Docker

The entire platform can be started with Docker Compose.

Services:

```text
prefect-server
app
worker
api
dashboard
```

### Start the project

From the project root:

```bash
docker compose up -d
```

Check the services:

```bash
docker compose ps
```

Expected services:

```text
prefect-server
app
worker
api
dashboard
```

---

## Accessing the services

| Service    | URL                        |
| ---------- | -------------------------- |
| Dashboard  | http://localhost:5173      |
| FastAPI    | http://localhost:8000      |
| Swagger UI | http://localhost:8000/docs |
| Prefect    | http://localhost:4200      |

---

## Running the pipeline

The full pipeline can be executed through the Prefect deployment.

The pipeline performs:

```text
GitHub extraction
      ↓
Bronze
      ↓
Silver
      ↓
Gold
```

The pipeline can also be executed directly during development:

```bash
python flows/run_pipeline.py
```

---

## Configuration

GitHub credentials and configuration are stored in `.env`.

Example configuration:

```env
GITHUB_USERNAME=your_github_username
GITHUB_TOKEN=your_github_token
```

Do not commit `.env` to Git.

Use `.env.example` as a template for local configuration.

---

## Project Structure

```text
github-data-platform/
│
├── api/
│   ├── routers/
│   │   └── metrics.py
│   ├── data.py
│   ├── main.py
│   └── schemas.py
│
├── dashboard/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ActivityChart.jsx
│   │   │   ├── AreaChart.jsx
│   │   │   ├── BarChart.jsx
│   │   │   ├── PieChart.jsx
│   │   │   ├── RepositoryTable.jsx
│   │   │   └── StatsCards.jsx
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── App.css
│   └── package.json
│
├── flows/
│   ├── extract_bronze.py
│   ├── build_silver.py
│   ├── build_gold.py
│   └── run_pipeline.py
│
├── tasks/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── storage/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── tests/
│
├── docker-compose.yml
├── dockerfile
├── prefect.yaml
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Data philosophy

This project intentionally separates raw ingestion from analytical datasets.

### Bronze

Raw data as close as possible to the GitHub API response.

### Silver

Cleaned and normalized data suitable for further processing.

### Gold

Business/engineering metrics optimized for consumption by the API and dashboard.

This separation makes the pipeline easier to:

* debug
* reproduce
* extend
* validate
* maintain

---

## Current dataset

The current real dataset contains:

* **9 repositories**
* **76 commits**
* **2 contributors**
* **0 open pull requests**

Deployment and lead-time metrics may currently be empty because the source GitHub account does not contain successful deployment runs or pull-request data for the extracted period.

Empty metrics represent the actual state of the source data and are not replaced with mock values.

---

## Development workflow

A typical development cycle is:

```text
1. Modify pipeline / API / dashboard
          ↓
2. Start Docker services
          ↓
3. Run or inspect the pipeline
          ↓
4. Validate Parquet datasets
          ↓
5. Test API endpoints
          ↓
6. Check dashboard
          ↓
7. Commit changes
```

Useful commands:

```bash
docker compose ps
```

```bash
docker compose logs api
```

```bash
docker compose logs worker
```

```bash
curl http://localhost:8000/metrics/summary
```

```bash
curl http://localhost:8000/metrics/repositories
```

---

## Troubleshooting

### API returns HTTP 500 while reading storage

First check that the files are accessible from inside the API container:

```bash
docker compose exec api ls -lh storage/silver/
```

If Docker temporarily loses access to the bind-mounted project directory, restart the Compose stack:

```bash
docker compose down
docker compose up -d
```

Then verify again:

```bash
docker compose exec api ls -lh storage/silver/
```

---

## Future Improvements

Possible future extensions include:

* additional GitHub metrics
* code review metrics
* deployment tracking improvements
* richer repository analytics
* automated pipeline scheduling
* improved dashboard filtering
* historical trend analysis
* automated tests for the complete pipeline
* data quality checks between Bronze, Silver, and Gold
* CI/CD integration

---

## License

This project is intended as a personal data engineering project and experimentation platform.

