import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.config import settings

# SQL schema for magic_tokens table
SCHEMA_MAGIC_TOKENS = """
CREATE TABLE IF NOT EXISTS magic_tokens (
    token_hash TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'used', 'expired'))
);
CREATE INDEX IF NOT EXISTS idx_magic_tokens_email ON magic_tokens(email);
CREATE INDEX IF NOT EXISTS idx_magic_tokens_status ON magic_tokens(status);
"""

# SQL schema for rate_limits table
SCHEMA_RATE_LIMITS = """
CREATE TABLE IF NOT EXISTS rate_limits (
    key TEXT PRIMARY KEY,
    window_start TEXT NOT NULL,
    count INTEGER DEFAULT 1
);
"""


def init_db() -> None:
    """Initialize the SQLite database with required tables."""
    # Ensure the directory exists
    db_path = Path(settings.sqlite_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with get_db() as db:
        db.executescript(SCHEMA_MAGIC_TOKENS)
        db.executescript(SCHEMA_RATE_LIMITS)


@contextmanager
def get_db():
    """Get a database connection with automatic commit/rollback."""
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_db_health() -> bool:
    """Check if the database is accessible and has required tables."""
    try:
        with get_db() as db:
            # Check we can query
            db.execute("SELECT 1")

            # Check tables exist
            cursor = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN (?, ?)",
                ("magic_tokens", "rate_limits"),
            )
            tables = [row["name"] for row in cursor.fetchall()]

            return len(tables) == 2
    except Exception:
        return False
