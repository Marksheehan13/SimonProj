# DeployHub — NASA APOD Integration Service

A Flask-based web service that integrates the NASA Astronomy Picture of the Day (APOD) API with a PostgreSQL database. Built for IS2209 as a demonstration of CI/CD, DevOps, and Agile practices.

---

## Tech Stack

- **Backend:** Python 3.11, Flask
- **Database:** PostgreSQL (Supabase)
- **External API:** NASA APOD API
- **CI/CD:** GitHub Actions
- **Containerisation:** Docker, Docker Compose
- **Registry:** GitHub Container Registry (GHCR)

---

## Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- A [Supabase](https://supabase.com) project (for PostgreSQL)
- A [NASA API key](https://api.nasa.gov/) (free)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/SimonProj.git
   cd SimonProj
   ```

2. **Create your `.env` file**
   ```bash
   cp .env.example .env
   ```
   Fill in your values:
   ```
   NASA_API_KEY=your_nasa_api_key_here
   DATABASE_URL=postgresql://username:password@host:5432/dbname
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```
   The app will be available at `http://localhost:5000`

4. **Or run directly with Python**
   ```bash
   pip install -r requirements.txt
   flask run
   ```

---

## Environment Variables

| Variable | Description |
|---|---|
| `NASA_API_KEY` | Your NASA API key from https://api.nasa.gov/ |
| `DATABASE_URL` | PostgreSQL connection string (e.g. from Supabase) |

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Main UI — NASA APOD viewer |
| `/api/today` | GET | Returns today's APOD as JSON, saves to DB |
| `/search?date=YYYY-MM-DD` | GET | Returns APOD for a specific date, saves to DB |
| `/history` | GET | Returns last 20 searches from the database |
| `/health` | GET | Health check — returns `{"status": "ok"}` |
| `/status` | GET | Checks DB and NASA API connectivity live |

---

## CI/CD Overview

The CI/CD pipeline is defined in `.github/workflows/ci.yml` and runs automatically on every pull request and push to `main`.

### CI Pipeline steps:
1. **Lint** — `ruff` checks code style
2. **Test** — `pytest` runs all tests with coverage report
3. **Build** — Docker image is built to verify it compiles
4. **Publish** — On merge to `main`, image is pushed to GHCR

### CD:
The app is deployed automatically to [Render/Fly.io] on every push to `main`.

### GitHub Actions Secrets required:
- `NASA_API_KEY` — set in repo Settings → Secrets → Actions

---

## Running Tests

```bash
pip install pytest pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Demo Steps

1. Open `http://localhost:5000` in your browser
2. The page loads today's NASA Astronomy Picture of the Day
3. Use the date picker to search for a specific date
4. Visit `/history` to see all past searches saved in the database
5. Visit `/health` to confirm the app is running
6. Visit `/status` to check live connectivity of all dependencies

---

## Deployment

Live URL: `https://<your-deployment-url>`

To deploy manually to Render:
1. Connect your GitHub repo to [Render](https://render.com)
2. Set environment variables in the Render dashboard
3. Render auto-deploys on every push to `main`

---

## Academic Integrity

This project was built as part of IS2209. All external libraries are listed in `requirements.txt`. The NASA APOD API is a free public API provided by NASA.
