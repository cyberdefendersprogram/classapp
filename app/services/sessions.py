"""Session management using JWT tokens."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)

# JWT configuration
ALGORITHM = "HS256"
SESSION_TTL_DAYS = 7
COOKIE_NAME = "session"


@dataclass
class SessionData:
    """Decoded session data."""

    email: str
    student_id: str
    exp: datetime


def create_session_token(email: str, student_id: str) -> str:
    """
    Create a JWT session token.

    Args:
        email: Student email
        student_id: Student ID

    Returns:
        Encoded JWT token
    """
    expires = datetime.utcnow() + timedelta(days=SESSION_TTL_DAYS)
    payload = {
        "email": email,
        "student_id": student_id,
        "exp": expires,
    }

    token = jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)
    logger.info("Created session for %s (student: %s)", email, student_id)
    return token


def verify_session_token(token: str) -> SessionData | None:
    """
    Verify and decode a JWT session token.

    Args:
        token: JWT token to verify

    Returns:
        SessionData if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])

        return SessionData(
            email=payload["email"],
            student_id=payload["student_id"],
            exp=datetime.fromtimestamp(payload["exp"]),
        )
    except JWTError as e:
        logger.warning("Invalid session token: %s", e)
        return None
    except KeyError as e:
        logger.warning("Malformed session token, missing key: %s", e)
        return None


def get_cookie_settings() -> dict:
    """
    Get cookie settings for session cookie.

    Returns:
        Dict of cookie settings
    """
    return {
        "key": COOKIE_NAME,
        "httponly": True,
        "secure": not settings.is_development,
        "samesite": "lax",
        "max_age": SESSION_TTL_DAYS * 24 * 60 * 60,  # seconds
    }
