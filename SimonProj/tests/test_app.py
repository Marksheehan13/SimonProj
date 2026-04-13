import pytest
from unittest.mock import patch, MagicMock
from app import app, init_db


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# --- /health ---

def test_health_endpoint_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


# --- /api/today ---

@patch("app.fetch_apod")
@patch("app.get_db")
def test_returns_joined_result_when_both_sources_available(mock_db, mock_fetch, client):
    mock_fetch.return_value = {
        "date": "2024-01-01",
        "title": "Test Galaxy",
        "url": "https://example.com/image.jpg",
        "explanation": "A test explanation.",
        "media_type": "image"
    }
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn

    response = client.get("/api/today")
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Test Galaxy"
    assert data["date"] == "2024-01-01"


@patch("app.fetch_apod")
def test_graceful_degradation_on_upstream_failure(mock_fetch, client):
    mock_fetch.return_value = None

    response = client.get("/api/today")
    assert response.status_code == 503
    data = response.get_json()
    assert "error" in data


# --- /search ---

@patch("app.fetch_apod")
@patch("app.get_db")
def test_search_returns_result_for_valid_date(mock_db, mock_fetch, client):
    mock_fetch.return_value = {
        "date": "2023-06-15",
        "title": "A Distant Nebula",
        "url": "https://example.com/nebula.jpg",
        "explanation": "A nebula far away.",
        "media_type": "image"
    }
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn

    response = client.get("/search?date=2023-06-15")
    assert response.status_code == 200
    data = response.get_json()
    assert data["date"] == "2023-06-15"


def test_search_returns_error_when_no_date(client):
    response = client.get("/search")
    assert response.status_code == 400
    assert "error" in response.get_json()


# --- /status ---

@patch("app.get_db")
@patch("app.requests.get")
def test_health_endpoint_reports_dependencies(mock_requests, mock_db, client):
    mock_conn = MagicMock()
    mock_db.return_value = mock_conn

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    response = client.get("/status")
    assert response.status_code == 200
    data = response.get_json()
    assert "database" in data["dependencies"]
    assert "nasa_api" in data["dependencies"]


# --- /history ---

@patch("app.get_db")
def test_history_returns_list(mock_db, client):
    mock_conn = MagicMock()
    mock_conn.execute.return_value.fetchall.return_value = [
        ("2024-01-01", "Test Galaxy", "2024-01-01 12:00:00")
    ]
    mock_db.return_value = mock_conn

    response = client.get("/history")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Test Galaxy"
