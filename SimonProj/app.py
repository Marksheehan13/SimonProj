import logging
import os
import time
import uuid

import psycopg
import requests
from dotenv import load_dotenv
from flask import Flask, g, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)

# --- Structured logging setup ---
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = g.get("request_id", "startup")
        except RuntimeError:
            record.request_id = "startup"
        return True

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '{"time": "%(asctime)s", "level": "%(levelname)s", "request_id": "%(request_id)s", "message": "%(message)s"}'
))
handler.addFilter(RequestIdFilter())

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# --- Config from environment ---
NASA_API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
NASA_BASE_URL = "https://api.nasa.gov/planetary/apod"
DATABASE_URL = os.environ.get("DATABASE_URL")


# --- DB helpers ---
def get_db():
    if "db" not in g:
        g.db = psycopg.connect(DATABASE_URL)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    """Create the searches table if it doesn't exist."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id SERIAL PRIMARY KEY,
                date TEXT NOT NULL,
                title TEXT,
                searched_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()


# --- Request lifecycle: attach request ID and log timing ---
@app.before_request
def before_request():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()
    logger.info(f"Request started: {request.method} {request.path}")

@app.after_request
def after_request(response):
    duration_ms = round((time.time() - g.start_time) * 1000, 2)
    logger.info(f"Request completed: status={response.status_code} duration_ms={duration_ms}")
    response.headers["X-Request-ID"] = g.request_id
    return response


# --- NASA API helper with retry/backoff ---
def fetch_apod(params: dict, retries: int = 3) -> dict:
    params["api_key"] = NASA_API_KEY
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(NASA_BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.warning(f"NASA API attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)
    return None


# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/today")
def get_today():
    data = fetch_apod({})
    if data is None:
        return jsonify({"error": "NASA API is currently unavailable. Please try again later."}), 503

    try:
        db = get_db()
        db.execute(
            "INSERT INTO searches (date, title) VALUES (%s, %s)",
            (data.get("date"), data.get("title"))
        )
        db.commit()
    except Exception as e:
        logger.warning(f"DB write failed: {e}")

    return jsonify(data)


@app.route("/search")
def search():
    date = request.args.get("date")
    if not date:
        return jsonify({"error": "No date provided. Use format YYYY-MM-DD"}), 400

    data = fetch_apod({"date": date})
    if data is None:
        return jsonify({"error": "NASA API is currently unavailable. Please try again later."}), 503

    try:
        db = get_db()
        db.execute(
            "INSERT INTO searches (date, title) VALUES (%s, %s)",
            (data.get("date"), data.get("title"))
        )
        db.commit()
    except Exception as e:
        logger.warning(f"DB write failed: {e}")

    return jsonify(data)


@app.route("/history")
def history():
    try:
        db = get_db()
        rows = db.execute(
            "SELECT date, title, searched_at FROM searches ORDER BY searched_at DESC LIMIT 20"
        ).fetchall()
        results = [{"date": r[0], "title": r[1], "searched_at": str(r[2])} for r in rows]
        return jsonify(results)
    except Exception as e:
        logger.error(f"DB read failed: {e}")
        return jsonify({"error": "Could not retrieve history"}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/status")
def status():
    results = {}

    try:
        db = get_db()
        db.execute("SELECT 1")
        results["database"] = "ok"
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        results["database"] = f"error: {str(e)}"

    try:
        resp = requests.get(
            NASA_BASE_URL,
            params={"api_key": NASA_API_KEY},
            timeout=5
        )
        results["nasa_api"] = "ok" if resp.status_code == 200 else f"error: HTTP {resp.status_code}"
    except Exception as e:
        results["nasa_api"] = f"error: {str(e)}"

    overall = "ok" if all(v == "ok" for v in results.values()) else "degraded"
    return jsonify({"status": overall, "dependencies": results}), 200


if __name__ == "__main__":
    if DATABASE_URL:
        init_db()
    app.run(debug=False)