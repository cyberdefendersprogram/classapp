# Class Portal

A lightweight course portal for ~30 students with Google Sheets as the backend.

## Features

### Implemented
- [x] FastAPI application scaffold
- [x] Configuration via environment variables
- [x] Docker containerization
- [x] Development environment with hot reload
- [x] SQLite for tokens and rate limiting
- [x] Health check endpoint (`/health`)
- [x] Google Sheets integration (with caching)
- [x] Data models (Student, Quiz, QuizSubmission)
- [x] Magic link authentication
- [x] Student account claiming
- [x] Onboarding flow
- [x] Quiz system with auto-grading
- [x] Admin analytics dashboard (per-question quiz performance)
- [x] Admin grading page (spreadsheet view of all student scores)
- [x] CSV export of grades

### Planned
- [ ] CI/CD with GitHub Actions
- [ ] Production deployment to DigitalOcean

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.12) |
| Database | Google Sheets + SQLite |
| Templates | Jinja2 |
| Auth | Magic links (JWT sessions) |
| Container | Docker |
| Hosting | DigitalOcean Droplet |

## Project Structure

```
classapp/
├── app/
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Settings (pydantic-settings)
│   ├── routers/           # Route handlers
│   ├── services/          # Business logic
│   ├── models/            # Data models
│   ├── db/                # Database (SQLite)
│   └── templates/         # Jinja2 templates
├── content/
│   └── quizzes/           # Quiz markdown files
├── tests/                 # Pytest tests
├── scripts/               # Utility scripts
├── nginx/                 # Nginx config
├── Dockerfile
├── docker-compose.yml     # Production
└── docker-compose.dev.yml # Development
```

## Development

### Prerequisites

- Python 3.12+
- Docker (optional, recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd classapp
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Option A: Run with Docker (recommended)**
   ```bash
   docker compose -f docker-compose.dev.yml up --build
   ```

4. **Option B: Run locally**
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements-dev.txt
   uvicorn app.main:app --reload
   ```

5. **Access the app**
   ```
   http://localhost:8000
   ```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | Yes | - | JWT signing key (32+ chars) |
| `BASE_URL` | Yes | - | Public URL of the app |
| `GOOGLE_SHEETS_ID` | Yes | - | Google Spreadsheet ID |
| `GOOGLE_SERVICE_ACCOUNT_PATH` | Yes | - | Path to service account JSON |
| `SMTP_HOST` | Yes | - | SMTP server hostname |
| `SMTP_PORT` | No | `587` | SMTP server port |
| `SMTP_USER` | Yes | - | SMTP username |
| `SMTP_PASS` | Yes | - | SMTP password |
| `ENV` | No | `development` | Environment (`development`/`production`) |
| `LOG_LEVEL` | No | `INFO` | Log level |
| `SQLITE_PATH` | No | `data/app.db` | SQLite database path |

## Testing

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_root.py -v
```

### Run tests in Docker
```bash
docker compose -f docker-compose.dev.yml run --rm app pytest
```

## Deployment

### Production Docker Compose

The `docker-compose.yml` is configured for production:

```bash
# On the server
docker compose pull
docker compose up -d
```

### Manual Deployment

1. **Build the image**
   ```bash
   docker build -t classapp .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name classapp \
     -p 127.0.0.1:8000:8000 \
     --env-file .env \
     -v /var/lib/classapp:/var/lib/classapp \
     classapp
   ```

### CI/CD (Planned)

GitHub Actions workflow will:
1. Run tests on pull requests
2. Build and push Docker image to GHCR on merge to `main`
3. SSH to droplet and deploy

## API Endpoints

### Currently Available

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Root endpoint (returns app info) |
| GET | `/health` | Health check (SQLite + Sheets status) |

### Authentication & User Routes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/request-link` | Request magic link |
| GET | `/auth/verify` | Verify magic link token |
| POST | `/auth/logout` | Logout |
| GET | `/claim` | Account claim form |
| POST | `/claim` | Submit claim |
| GET | `/onboarding` | Onboarding form |
| POST | `/onboarding` | Submit onboarding |
| GET | `/home` | Dashboard |
| GET | `/quizzes` | Quiz list |
| GET | `/quiz/{id}` | Quiz form |
| POST | `/quiz/{id}` | Submit quiz |
| GET | `/me` | Profile |

### Admin Routes (requires `admin_email` in Config sheet)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/analytics` | Quiz analytics overview |
| GET | `/admin/quiz/{id}` | Per-question analytics for a quiz |
| GET | `/admin/grading` | Grading table (all students x all quizzes) |
| GET | `/admin/grading/csv` | Download grades as CSV |

## Admin Configuration

The admin dashboard requires setting `admin_email` in the Config sheet of your Google Spreadsheet:

| key | value |
|-----|-------|
| admin_email | admin@example.com |

Only the user with this email can access admin pages:

- **Analytics** (`/admin/analytics`) - Quiz completion rates and average scores
- **Quiz Details** (`/admin/quiz/{id}`) - Per-question analytics with answer distribution
- **Grading** (`/admin/grading`) - Spreadsheet view of all students' best scores per quiz
- **CSV Export** (`/admin/grading/csv`) - Download grades as CSV file

Admin users see an "Admin" link in the navigation bar on all pages.

## Documentation

- [SPEC.md](./SPEC.md) - Technical specification
- [PLAN.md](./PLAN.md) - Implementation plan

## License

Private - All rights reserved
