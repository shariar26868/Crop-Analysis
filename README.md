# Agriculture DB API

Farm Performance & Crop Market Intelligence API built with **FastAPI**, **SQLAlchemy**, **Pandas**, Redis caching, and Celery background processing.

---

## Tech Stack

| Layer | Tool |
|---|---|
| Database | MySQL (`agriculture_db`) |
| DB Connection | SQLAlchemy + PyMySQL |
| Data Processing | Python + Pandas |
| API Framework | FastAPI |
| API Server | Uvicorn |
| Caching | Redis (optional — graceful fallback if unavailable) |
| Background Tasks | Celery + Redis |

---

## Prerequisites

- Python 3.9+
- MySQL database access (credentials provided separately)
- Redis (optional — app works without it)

---

## Setup & Run

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd weGrow_Assignment
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
HOST=<db_host>
PORT=3306
DB=agriculture_db
USER=<db_user>
PASSWORD=<db_password>
ALLOWED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
RATE_LIMIT=60 per minute
APP_ENV=development
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60
ADMIN_USER=admin
ADMIN_PASS=adminpass
REDIS_URL=redis://localhost:6379/0
CACHE_DEFAULT_EXPIRE=120
PRIME_CACHE_INTERVAL=600
LOG_LEVEL=INFO
API_URL=http://localhost:8000
```

### 4. Run the API server

```bash
python main.py
```

Or using Uvicorn directly (with auto-reload for development):

```bash
uvicorn main:app --reload
```

The API will be available at:
- **API:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/docs`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## Run with Docker (Recommended)

Starts the API, Redis, Celery worker, and Celery beat scheduler together.

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000/docs`.

---

## Verification Tests

An automated test suite is provided to verify all 8 endpoints work correctly under various filter combinations. You can run it locally:

```bash
python run_tests.py
```

---

## API Endpoints

### Report 1 — Farm Performance

| Method | Endpoint | Description |
|---|---|---|
| GET | `/farms/summary` | Farm revenue, profit, cost, and loss percentages |
| GET | `/farms/{farm_id}/performance` | Detailed breakdown for a single farm |
| GET | `/farms/top` | Top N farms ranked by profit, revenue, or yield |
| GET | `/farms/loss-analysis` | Post-harvest loss analysis by region, season, crop |

### Report 2 — Crop & Market Intelligence

| Method | Endpoint | Description |
|---|---|---|
| GET | `/crops/yield-efficiency` | Actual yield vs benchmark per crop |
| GET | `/crops/seasonal-trend` | Seasonal revenue trends per crop |
| GET | `/markets/price-comparison` | Market channel price comparison |
| GET | `/crops/quality-breakdown` | Quality grade and pesticide residue breakdown |

---

## Filter Reference

| Filter | Accepted Values |
|---|---|
| `region` | Dhaka, Chittagong, Sylhet, Rajshahi, Khulna, Rangpur, Barisal, Mymensingh |
| `farm_type` | Small, Medium, Large, Commercial |
| `crop_category` | Cereal, Vegetable, Fruit, Pulse, Oilseed, Cash Crop, Spice |
| `season` | Spring, Summer, Autumn, Winter |
| `market_type` | Local, Wholesale, Export, Retail, Government Procurement |
| `price_tier` | Low, Medium, High, Premium |
| `quality_grade` | A, B, C, D |
| `pesticide_residue` | None, Trace, Low, High |
| `water_requirement` | Low, Medium, High |
| `year` | 2022, 2023, 2024 |
| `quarter` | 1, 2, 3, 4 |
| `metric` | profit, revenue, yield |

> Filters are **case-insensitive** — `dhaka`, `Dhaka`, `DHAKA` all work.
> Invalid filter values return **HTTP 422** with a clear error message.

---

## Example Requests

```bash
# Top 5 farms by profit in Rajshahi
GET /farms/top?metric=profit&region=Rajshahi&limit=5

# Loss analysis for Winter 2023
GET /farms/loss-analysis?season=Winter&year=2023

# Cereal yield efficiency in 2023
GET /crops/yield-efficiency?crop_category=Cereal&year=2023

# Export market prices for cereals
GET /markets/price-comparison?market_type=Export&crop_category=Cereal
```

---

## Authentication

Admin endpoints require a JWT token.

### Get a token

```bash
curl -X POST http://localhost:8000/auth/token \
  -d "username=admin&password=adminpass"
```

Response:
```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

Use the token:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/admin/cache/flush \
  -X POST -H "Content-Type: application/json" \
  -d '{"prefix": "farms:"}'
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `HOST` | MySQL host | `localhost` |
| `PORT` | MySQL port | `3306` |
| `DB` | Database name | `agriculture_db` |
| `USER` | Database user | `user` |
| `PASSWORD` | Database password | `password` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:8000` |
| `SECRET_KEY` | JWT secret key | `CHANGE_ME_IN_PRODUCTION` |
| `ADMIN_USER` | Admin username | `admin` |
| `ADMIN_PASS` | Admin password | `adminpass` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CACHE_DEFAULT_EXPIRE` | Cache TTL in seconds | `120` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SENTRY_DSN` | Optional Sentry DSN | `` |
