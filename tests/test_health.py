"""Tests for health endpoint."""

from unittest.mock import patch


def test_health_returns_200_when_healthy(client):
    """Test that health endpoint returns 200 when all checks pass."""
    with patch("app.routers.health.get_sheets_client") as mock_sheets:
        mock_sheets.return_value.check_connection.return_value = True

        response = client.get("/health")

        assert response.status_code == 200


def test_health_returns_status_ok(client):
    """Test that health endpoint returns status ok when healthy."""
    with patch("app.routers.health.get_sheets_client") as mock_sheets:
        mock_sheets.return_value.check_connection.return_value = True

        response = client.get("/health")
        data = response.json()

        assert data["status"] == "ok"


def test_health_returns_version(client):
    """Test that health endpoint returns version."""
    with patch("app.routers.health.get_sheets_client") as mock_sheets:
        mock_sheets.return_value.check_connection.return_value = True

        response = client.get("/health")
        data = response.json()

        assert "version" in data
        assert data["version"] == "1.0.0"


def test_health_checks_sqlite(client):
    """Test that health endpoint checks SQLite."""
    with patch("app.routers.health.get_sheets_client") as mock_sheets:
        mock_sheets.return_value.check_connection.return_value = True

        response = client.get("/health")
        data = response.json()

        assert "checks" in data
        assert "sqlite" in data["checks"]
        assert data["checks"]["sqlite"] is True


def test_health_checks_sheets(client):
    """Test that health endpoint checks Sheets connection."""
    with patch("app.routers.health.get_sheets_client") as mock_sheets:
        mock_sheets.return_value.check_connection.return_value = True

        response = client.get("/health")
        data = response.json()

        assert "sheets" in data["checks"]
        assert data["checks"]["sheets"] is True


def test_health_returns_503_when_sheets_down(client):
    """Test that health returns 503 when sheets check fails."""
    with patch("app.routers.health.get_sheets_client") as mock_sheets:
        mock_sheets.return_value.check_connection.return_value = False

        response = client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["checks"]["sheets"] is False


def test_health_returns_degraded_status(client):
    """Test that health returns degraded when any check fails."""
    with patch("app.routers.health.get_sheets_client") as mock_sheets:
        mock_sheets.return_value.check_connection.return_value = False

        response = client.get("/health")
        data = response.json()

        assert data["status"] == "degraded"
