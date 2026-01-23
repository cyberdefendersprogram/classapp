# Class Portal v1 — Implementation Plan

**Goal**: Incremental implementation with tests at each phase, deployable to DigitalOcean.

---

## Project Structure

```
classapp/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Settings (pydantic-settings)
│   ├── dependencies.py         # Shared dependencies
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py             # Magic link, login, logout
│   │   ├── claim.py            # Account claiming
│   │   ├── onboarding.py       # Onboarding form
│   │   ├── quizzes.py          # Quiz list and submission
│   │   ├── pages.py            # Home, profile pages
│   │   └── health.py           # Health check
│   ├── services/
│   │   ├── __init__.py
│   │   ├── sheets.py           # Google Sheets client
│   │   ├── email.py            # SMTP client
│   │   ├── tokens.py           # Magic token logic
│   │   ├── sessions.py         # JWT session handling
│   │   ├── cache.py            # In-memory TTL cache
│   │   └── grading.py          # Quiz auto-grader
│   ├── models/
│   │   ├── __init__.py
│   │   ├── student.py          # Student dataclass
│   │   ├── quiz.py             # Quiz/Question dataclasses
│   │   └── schemas.py          # Pydantic request/response
│   ├── db/
│   │   ├── __init__.py
│   │   └── sqlite.py           # SQLite setup + queries
│   └── templates/
│       ├── base.html
│       ├── signin.html
│       ├── claim.html
│       ├── onboarding.html
│       ├── home.html
│       ├── quizzes.html
│       ├── quiz.html
│       └── me.html
├── content/
│   └── quizzes/                # Quiz markdown files
│       └── 001-sample.md
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures
│   ├── test_health.py
│   ├── test_tokens.py
│   ├── test_rate_limit.py
│   ├── test_auth.py
│   ├── test_claim.py
│   ├── test_onboarding.py
│   ├── test_quiz_parser.py
│   ├── test_grading.py
│   └── test_quizzes.py
├── scripts/
│   ├── provision.sh            # Droplet setup
│   └── seed_sheets.py          # Test data seeder
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       ├── test.yml            # Run tests on PR
│       └── deploy.yml          # Deploy on main
└── nginx/
    └── classapp.conf
```

---

## Phase 0: Project Scaffolding

**Goal**: Runnable FastAPI app in Docker, basic project structure.

### 0.1 Tasks

- [ ] Create directory structure
- [ ] Create `pyproject.toml`
- [ ] Create `requirements.txt`:
  ```
  fastapi==0.115.0
  uvicorn[standard]==0.32.0
  python-jose[cryptography]==3.3.0
  gspread==6.1.0
  google-auth==2.36.0
  jinja2==3.1.4
  python-multipart==0.0.18
  aiosmtplib==3.0.2
  pydantic-settings==2.6.0
  ```
- [ ] Create `requirements-dev.txt`:
  ```
  pytest==8.3.0
  pytest-asyncio==0.24.0
  pytest-cov==6.0.0
  httpx==0.28.0
  ```
- [ ] Create `app/main.py` with minimal FastAPI app
- [ ] Create `app/config.py` with pydantic-settings
- [ ] Create `Dockerfile`
- [ ] Create `docker-compose.yml` and `docker-compose.dev.yml`
- [ ] Create `.env.example`
- [ ] Create `.gitignore`

### 0.2 Files

**pyproject.toml**
```toml
[project]
name = "classapp"
version = "1.0.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**app/main.py**
```python
from fastapi import FastAPI
from app.config import settings

app = FastAPI(title=settings.app_name)

@app.get("/")
async def root():
    return {"message": "Class Portal"}
```

**app/config.py**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Class Portal"
    env: str = "development"
    secret_key: str
    base_url: str

    # Google Sheets
    google_sheets_id: str
    google_service_account_path: str

    # SMTP
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str
    smtp_pass: str

    # SQLite
    sqlite_path: str = "/var/lib/classapp/app.db"

    class Config:
        env_file = ".env"

settings = Settings()
```

**Dockerfile**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml**
```yaml
services:
  app:
    image: ghcr.io/USERNAME/classapp:latest
    ports:
      - "127.0.0.1:8000:8000"
    env_file:
      - ./env/.env
    volumes:
      - /var/lib/classapp:/var/lib/classapp
      - /etc/classapp:/etc/classapp:ro
    restart: unless-stopped
```

**docker-compose.dev.yml**
```yaml
services:
  app:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - .:/app
      - ./data:/var/lib/classapp
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 0.3 Verification

```bash
# Local
docker compose -f docker-compose.dev.yml up --build
curl http://localhost:8000/
# → {"message": "Class Portal"}
```

### 0.4 Tests

```python
# tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
```

---

## Phase 1: SQLite + Health Check

**Goal**: SQLite initialized, health endpoint works.

### 1.1 Tasks

- [ ] Create `app/db/sqlite.py` with table creation
- [ ] Create `app/routers/health.py`
- [ ] Add startup event to initialize DB
- [ ] Wire health router to main app

### 1.2 Files

**app/db/sqlite.py**
```python
import sqlite3
from contextlib import contextmanager
from app.config import settings

def init_db():
    with get_db() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS magic_tokens (
                token_hash TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                status TEXT DEFAULT 'pending'
            );
            CREATE INDEX IF NOT EXISTS idx_tokens_email ON magic_tokens(email);

            CREATE TABLE IF NOT EXISTS rate_limits (
                key TEXT PRIMARY KEY,
                window_start TEXT NOT NULL,
                count INTEGER DEFAULT 1
            );
        """)

@contextmanager
def get_db():
    conn = sqlite3.connect(settings.sqlite_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
```

**app/routers/health.py**
```python
from fastapi import APIRouter
from app.db.sqlite import get_db

router = APIRouter()

@router.get("/health")
async def health():
    checks = {"sqlite": False, "sheets": False}

    # Check SQLite
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        checks["sqlite"] = True
    except Exception:
        pass

    # Sheets check added in Phase 2

    status = "ok" if all(checks.values()) else "degraded"
    code = 200 if status == "ok" else 503

    return {"status": status, "checks": checks, "version": "1.0.0"}
```

### 1.3 Tests

```python
# tests/test_health.py
def test_health_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"]["sqlite"] == True
```

---

## Phase 2: Google Sheets Integration

**Goal**: Read/write to Sheets, caching works.

### 2.1 Tasks

- [ ] Create `app/services/sheets.py` with gspread client
- [ ] Create `app/services/cache.py` with TTL cache
- [ ] Implement all Sheets methods (see below)
- [ ] Update health check to verify Sheets connection
- [ ] Create `scripts/seed_sheets.py` for test data

### 2.2 Sheets Client Methods

```python
# app/services/sheets.py
class SheetsClient:
    def get_student_by_email(self, email: str) -> Student | None
    def get_student_by_id(self, student_id: str) -> Student | None
    def claim_student(self, student_id: str, claim_code: str, email: str) -> bool
    def update_student(self, student_id: str, **fields) -> bool
    def get_config(self, key: str) -> str | None
    def get_quizzes(self) -> list[Quiz]
    def get_quiz_submissions(self, student_id: str, quiz_id: str) -> list[Submission]
    def append_onboarding_response(self, data: dict) -> None
    def append_quiz_submission(self, data: dict) -> None
    def append_magic_link_request(self, data: dict) -> None
```

### 2.3 Cache Implementation

```python
# app/services/cache.py
from functools import wraps
from time import time

_cache = {}

def cached(ttl_seconds: int):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            now = time()
            if key in _cache:
                value, expires = _cache[key]
                if now < expires:
                    return value
            result = func(*args, **kwargs)
            _cache[key] = (result, now + ttl_seconds)
            return result
        return wrapper
    return decorator

def invalidate(prefix: str):
    keys_to_delete = [k for k in _cache if k[0].startswith(prefix)]
    for k in keys_to_delete:
        del _cache[k]
```

### 2.4 Tests

```python
# tests/test_sheets.py (with mocked gspread)
def test_get_student_by_email(mock_sheets):
    student = mock_sheets.get_student_by_email("test@example.com")
    assert student.email == "test@example.com"

def test_get_student_not_found(mock_sheets):
    student = mock_sheets.get_student_by_email("unknown@example.com")
    assert student is None
```

---

## Phase 3: Magic Link Authentication

**Goal**: Request magic link, validate token, create session.

### 3.1 Tasks

- [ ] Create `app/services/tokens.py`
- [ ] Create `app/services/email.py`
- [ ] Create `app/services/sessions.py`
- [ ] Create `app/routers/auth.py`
- [ ] Implement rate limiting
- [ ] Add templates: `signin.html`

### 3.2 Token Service

```python
# app/services/tokens.py
import secrets
import hashlib
from datetime import datetime, timedelta
from app.db.sqlite import get_db

def create_magic_token(email: str, ttl_minutes: int = 15) -> str:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)

    with get_db() as db:
        db.execute("""
            INSERT INTO magic_tokens (token_hash, email, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        """, (token_hash, email, datetime.utcnow().isoformat(), expires_at.isoformat()))

    return token

def validate_magic_token(token: str) -> str | None:
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    with get_db() as db:
        row = db.execute("""
            SELECT email, expires_at, status FROM magic_tokens
            WHERE token_hash = ?
        """, (token_hash,)).fetchone()

        if not row:
            return None
        if row["status"] != "pending":
            return None
        if datetime.fromisoformat(row["expires_at"]) < datetime.utcnow():
            return None

        # Mark as used
        db.execute("""
            UPDATE magic_tokens SET status = 'used', used_at = ?
            WHERE token_hash = ?
        """, (datetime.utcnow().isoformat(), token_hash))

        return row["email"]
```

### 3.3 Session Service

```python
# app/services/sessions.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from app.config import settings

def create_session_token(email: str, student_id: str) -> str:
    payload = {
        "email": email,
        "student_id": student_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def verify_session_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None
```

### 3.4 Auth Routes

```python
# app/routers/auth.py
@router.post("/auth/request-link")
async def request_link(email: str = Form(...)):
    # Rate limit check
    # Create token
    # Send email
    # Log to Sheets
    # Return success (same message for known/unknown emails)

@router.get("/auth/verify")
async def verify(token: str, response: Response):
    # Validate token
    # Look up student by email
    # If found and claimed → create session, redirect to /home
    # If not found → redirect to /claim with temp token

@router.post("/auth/logout")
async def logout(response: Response):
    # Clear session cookie
    # Redirect to /
```

### 3.5 Tests

```python
# tests/test_tokens.py
def test_create_and_validate_token():
    token = create_magic_token("test@example.com")
    email = validate_magic_token(token)
    assert email == "test@example.com"

def test_token_single_use():
    token = create_magic_token("test@example.com")
    validate_magic_token(token)  # First use
    email = validate_magic_token(token)  # Second use
    assert email is None

def test_token_expiry():
    token = create_magic_token("test@example.com", ttl_minutes=-1)
    email = validate_magic_token(token)
    assert email is None
```

---

## Phase 4: Claim Flow

**Goal**: New students can claim their account with student_id + claim_code.

### 4.1 Tasks

- [ ] Create `app/routers/claim.py`
- [ ] Add template: `claim.html`
- [ ] Implement claim validation logic
- [ ] Update student record on successful claim

### 4.2 Claim Route

```python
# app/routers/claim.py
@router.get("/claim")
async def claim_form(request: Request, token: str):
    # Verify token is valid (not magic token, but a short-lived claim token)
    # Show form

@router.post("/claim")
async def claim_submit(
    student_id: str = Form(...),
    claim_code: str = Form(...),
    email: str = Form(...)  # From hidden field
):
    # Validate student exists
    # Validate claim_code matches
    # Validate not already claimed
    # Update student: set email, claimed_at
    # Create session
    # Redirect to /onboarding
```

### 4.3 Tests

```python
# tests/test_claim.py
def test_claim_success(client, mock_sheets):
    response = client.post("/claim", data={
        "student_id": "stu_001",
        "claim_code": "ABC123",
        "email": "new@example.com"
    })
    assert response.status_code == 302
    assert "/onboarding" in response.headers["location"]

def test_claim_wrong_code(client, mock_sheets):
    response = client.post("/claim", data={
        "student_id": "stu_001",
        "claim_code": "WRONG",
        "email": "new@example.com"
    })
    assert response.status_code == 400

def test_claim_already_claimed(client, mock_sheets):
    # Student already has email set
    response = client.post("/claim", data={
        "student_id": "stu_002",
        "claim_code": "DEF456",
        "email": "another@example.com"
    })
    assert response.status_code == 400
```

---

## Phase 5: Onboarding

**Goal**: Claimed students complete onboarding form.

### 5.1 Tasks

- [ ] Create `app/routers/onboarding.py`
- [ ] Add template: `onboarding.html`
- [ ] Write responses to Sheets
- [ ] Add middleware to redirect non-onboarded users

### 5.2 Onboarding Route

```python
# app/routers/onboarding.py
@router.get("/onboarding")
async def onboarding_form(request: Request):
    # Check session
    # Check if already onboarded → redirect to /home
    # Show form

@router.post("/onboarding")
async def onboarding_submit(
    request: Request,
    preferred_name: str = Form(...),
    pronouns: str = Form(""),
    hobbies: str = Form(""),
    computer_experience: str = Form(""),
    security_experience: str = Form(""),
    goals: str = Form(""),
    support_needs: str = Form("")
):
    # Validate preferred_name not empty
    # Update Students row
    # Append to Onboarding_Responses (one row per field)
    # Invalidate cache
    # Redirect to /home
```

### 5.3 Tests

```python
# tests/test_onboarding.py
def test_onboarding_success(authed_client, mock_sheets):
    response = authed_client.post("/onboarding", data={
        "preferred_name": "Alex",
        "pronouns": "they/them",
        "goals": "Learn security"
    })
    assert response.status_code == 302
    assert mock_sheets.update_student.called
    assert mock_sheets.append_onboarding_response.called

def test_onboarding_missing_name(authed_client):
    response = authed_client.post("/onboarding", data={
        "preferred_name": ""
    })
    assert response.status_code == 400
```

---

## Phase 6: Quiz System

**Goal**: Parse quizzes, display, submit, auto-grade.

### 6.1 Tasks

- [ ] Create `app/models/quiz.py` with dataclasses
- [ ] Create quiz parser for markdown
- [ ] Create `app/services/grading.py`
- [ ] Create `app/routers/quizzes.py`
- [ ] Add templates: `quizzes.html`, `quiz.html`
- [ ] Create sample quiz in `content/quizzes/001-sample.md`

### 6.2 Quiz Models

```python
# app/models/quiz.py
from dataclasses import dataclass

@dataclass
class Question:
    id: str
    type: str  # mcq_single, mcq_multi, numeric, short_text
    text: str
    points: int
    options: list[str] | None = None  # For MCQ
    correct: list[str] | str | None = None  # Answer(s)

@dataclass
class Quiz:
    id: str
    title: str
    questions: list[Question]
    total_points: int
```

### 6.3 Quiz Parser

```python
# app/services/quiz_parser.py
import re
import yaml

def parse_quiz(content: str, quiz_id: str) -> Quiz:
    # Split frontmatter and body
    # Parse YAML for title
    # Find all ## Q{n} headers
    # Parse each question based on type
    # Return Quiz object
```

### 6.4 Grading Service

```python
# app/services/grading.py
def grade_quiz(quiz: Quiz, answers: dict) -> dict:
    results = {}
    total_score = 0

    for q in quiz.questions:
        answer = answers.get(q.id)
        correct, points = grade_question(q, answer)
        results[q.id] = {
            "correct": correct,
            "points": points,
            "max": q.points
        }
        total_score += points

    return {
        "questions": results,
        "score": total_score,
        "max_score": quiz.total_points
    }

def grade_question(question: Question, answer) -> tuple[bool, int]:
    if question.type == "mcq_single":
        correct = answer == question.correct
    elif question.type == "mcq_multi":
        correct = set(answer or []) == set(question.correct)
    elif question.type == "numeric":
        correct = str(answer) == str(question.correct)
    elif question.type == "short_text":
        correct = (answer or "").strip().lower() == question.correct.strip().lower()
    else:
        correct = False

    return correct, question.points if correct else 0
```

### 6.5 Quiz Routes

```python
# app/routers/quizzes.py
@router.get("/quizzes")
async def list_quizzes(request: Request):
    # Get quizzes from Sheets
    # Filter by open_at/close_at
    # Get submission counts per quiz for this student
    # Render list

@router.get("/quiz/{quiz_id}")
async def quiz_form(request: Request, quiz_id: str):
    # Check quiz exists and is open
    # Check attempts remaining
    # Parse quiz content
    # Render form

@router.post("/quiz/{quiz_id}")
async def quiz_submit(request: Request, quiz_id: str):
    # Validate quiz is open
    # Validate attempts remaining
    # Parse answers from form
    # Grade quiz
    # Save to Quiz_Submissions
    # Show results
```

### 6.6 Tests

```python
# tests/test_quiz_parser.py
def test_parse_mcq_single():
    content = """
---
title: Test Quiz
---

## Q1 [mcq_single, 2pts]

What is 1+1?

- [ ] 1
- [x] 2
- [ ] 3
"""
    quiz = parse_quiz(content, "q001")
    assert quiz.title == "Test Quiz"
    assert len(quiz.questions) == 1
    assert quiz.questions[0].type == "mcq_single"
    assert quiz.questions[0].correct == "2"

# tests/test_grading.py
def test_grade_mcq_single_correct():
    q = Question(id="q1", type="mcq_single", text="?", points=2, correct="B")
    correct, points = grade_question(q, "B")
    assert correct == True
    assert points == 2

def test_grade_mcq_multi_partial():
    q = Question(id="q1", type="mcq_multi", text="?", points=3, correct=["A", "C"])
    correct, points = grade_question(q, ["A"])  # Missing C
    assert correct == False
    assert points == 0
```

---

## Phase 7: UI Templates

**Goal**: All screens render, mobile-friendly.

### 7.1 Tasks

- [ ] Create `templates/base.html` with layout and CSS
- [ ] Create all page templates
- [ ] Add flash message support
- [ ] Test on mobile viewport

### 7.2 Base Template

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Class Portal{% endblock %}</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: system-ui, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 1rem;
            line-height: 1.6;
        }
        .flash { padding: 1rem; margin: 1rem 0; border-radius: 4px; }
        .flash.error { background: #fee; color: #c00; }
        .flash.success { background: #efe; color: #060; }
        input, select, textarea, button {
            width: 100%;
            padding: 0.75rem;
            margin: 0.5rem 0;
            font-size: 1rem;
        }
        button { background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
            <div class="flash {{ category }}">{{ message }}</div>
        {% endfor %}
    {% endwith %}

    {% block content %}{% endblock %}
</body>
</html>
```

### 7.3 Template List

| Template | Content |
|----------|---------|
| `signin.html` | Email input, submit button |
| `claim.html` | student_id + claim_code inputs |
| `onboarding.html` | All onboarding fields |
| `home.html` | Welcome message, nav links |
| `quizzes.html` | Quiz cards with status |
| `quiz.html` | Questions rendered as form |
| `me.html` | Profile view, edit name |

---

## Phase 8: Deployment

**Goal**: Push to main → live on droplet.

### 8.1 Provisioning Script

```bash
#!/bin/bash
# scripts/provision.sh

set -e

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Nginx
apt install -y nginx

# Install certbot
apt install -y certbot python3-certbot-nginx

# Configure firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# Create directories
mkdir -p /opt/classapp/env
mkdir -p /var/lib/classapp
mkdir -p /etc/classapp

# Set permissions
chmod 700 /opt/classapp/env
chmod 700 /etc/classapp

echo "Provisioning complete. Next steps:"
echo "1. Copy .env to /opt/classapp/env/"
echo "2. Copy service-account.json to /etc/classapp/"
echo "3. Copy docker-compose.yml to /opt/classapp/"
echo "4. Copy nginx config to /etc/nginx/sites-available/"
echo "5. Run: certbot --nginx -d yourdomain.com"
echo "6. Run: cd /opt/classapp && docker compose up -d"
```

### 8.2 GitHub Actions - Test

```yaml
# .github/workflows/test.yml
name: Test

on:
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests
        run: pytest --cov=app tests/
```

### 8.3 GitHub Actions - Deploy

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to droplet
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.DROPLET_HOST }}
          username: root
          key: ${{ secrets.DROPLET_SSH_KEY }}
          script: |
            cd /opt/classapp
            docker compose pull
            docker compose up -d
```

### 8.4 Nginx Config

```nginx
# nginx/classapp.conf
server {
    listen 80;
    server_name class.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name class.example.com;

    ssl_certificate /etc/letsencrypt/live/class.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/class.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 8.5 Deployment Checklist

**Pre-deploy:**
- [ ] All tests pass locally
- [ ] `.env.example` has all variables
- [ ] Google service account created and shared with spreadsheet
- [ ] Domain DNS points to droplet IP

**On droplet:**
- [ ] Run `provision.sh`
- [ ] Copy `.env` to `/opt/classapp/env/.env`
- [ ] Copy `service-account.json` to `/etc/classapp/`
- [ ] Copy `docker-compose.yml` to `/opt/classapp/`
- [ ] Enable nginx site: `ln -s /etc/nginx/sites-available/classapp.conf /etc/nginx/sites-enabled/`
- [ ] Get TLS cert: `certbot --nginx -d class.example.com`
- [ ] Start app: `cd /opt/classapp && docker compose up -d`

**Post-deploy:**
- [ ] Check `/health` returns OK
- [ ] Test magic link email arrives
- [ ] Complete full claim → onboarding → quiz flow

---

## Milestones

| # | Milestone | Phases | Deliverable |
|---|-----------|--------|-------------|
| M1 | Bootable | 0-1 | App runs, /health works |
| M2 | Sheets | 2 | Can read/write Sheets |
| M3 | Auth | 3-4 | Magic link + claim works |
| M4 | Complete | 5-6 | Onboarding + quizzes work |
| M5 | Polished | 7 | UI complete, mobile-ready |
| M6 | Live | 8 | Deployed with TLS |

---

## Testing Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_grading.py -v

# Run in Docker
docker compose -f docker-compose.dev.yml run --rm app pytest
```

---

**End of Implementation Plan**
