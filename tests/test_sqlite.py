import os
import tempfile

import pytest

from app.db.sqlite import check_db_health, get_db, init_db


@pytest.fixture
def temp_db(monkeypatch):
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name

    monkeypatch.setattr("app.db.sqlite.settings.sqlite_path", temp_path)
    monkeypatch.setattr("app.config.settings.sqlite_path", temp_path)

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_init_db_creates_tables(temp_db):
    """Test that init_db creates required tables."""
    init_db()

    with get_db() as db:
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [row["name"] for row in cursor.fetchall()]

    assert "magic_tokens" in tables
    assert "rate_limits" in tables


def test_init_db_is_idempotent(temp_db):
    """Test that init_db can be called multiple times."""
    init_db()
    init_db()  # Should not raise

    with get_db() as db:
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='magic_tokens'"
        )
        assert cursor.fetchone() is not None


def test_check_db_health_returns_true(temp_db):
    """Test that check_db_health returns True when DB is healthy."""
    init_db()
    assert check_db_health() is True


def test_check_db_health_returns_false_without_tables(temp_db):
    """Test that check_db_health returns False when tables missing."""
    # Create empty DB without tables
    with get_db() as db:
        db.execute("SELECT 1")

    assert check_db_health() is False


def test_get_db_commits_on_success(temp_db):
    """Test that get_db commits changes on success."""
    init_db()

    with get_db() as db:
        db.execute(
            "INSERT INTO rate_limits (key, window_start, count) VALUES (?, ?, ?)",
            ("test_key", "2025-01-01T00:00:00", 1),
        )

    # Verify data persisted
    with get_db() as db:
        cursor = db.execute("SELECT * FROM rate_limits WHERE key = ?", ("test_key",))
        row = cursor.fetchone()
        assert row is not None
        assert row["count"] == 1


def test_get_db_rolls_back_on_error(temp_db):
    """Test that get_db rolls back on error."""
    init_db()

    with pytest.raises(Exception):
        with get_db() as db:
            db.execute(
                "INSERT INTO rate_limits (key, window_start, count) VALUES (?, ?, ?)",
                ("rollback_test", "2025-01-01T00:00:00", 1),
            )
            raise Exception("Simulated error")

    # Verify data was rolled back
    with get_db() as db:
        cursor = db.execute(
            "SELECT * FROM rate_limits WHERE key = ?", ("rollback_test",)
        )
        assert cursor.fetchone() is None


def test_magic_tokens_table_schema(temp_db):
    """Test that magic_tokens table has correct schema."""
    init_db()

    with get_db() as db:
        # Insert a valid row
        db.execute(
            """
            INSERT INTO magic_tokens (token_hash, email, created_at, expires_at, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("hash123", "test@example.com", "2025-01-01T00:00:00", "2025-01-01T00:15:00", "pending"),
        )

        cursor = db.execute("SELECT * FROM magic_tokens WHERE token_hash = ?", ("hash123",))
        row = cursor.fetchone()

        assert row["token_hash"] == "hash123"
        assert row["email"] == "test@example.com"
        assert row["status"] == "pending"
        assert row["used_at"] is None


def test_magic_tokens_status_constraint(temp_db):
    """Test that magic_tokens status has CHECK constraint."""
    init_db()

    with pytest.raises(Exception):
        with get_db() as db:
            db.execute(
                """
                INSERT INTO magic_tokens (token_hash, email, created_at, expires_at, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("hash456", "test@example.com", "2025-01-01T00:00:00", "2025-01-01T00:15:00", "invalid_status"),
            )
