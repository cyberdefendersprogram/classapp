# Class Portal v1 — Technical & Product Specification

**Version**: 1.1
**Stack**: FastAPI + Google Sheets + SQLite + Docker + DigitalOcean

---

## 1. Purpose

A lightweight course portal for ~30 students with minimal cost and operational complexity.

**Goals**:
- Google Sheets as the system of record (human-readable)
- Markdown for all instructional content
- Single instructor operation with minimal overhead
- ~$6/month infrastructure cost

**This spec covers**:
- Authentication and onboarding
- Quiz system with auto-grading
- Data models (Sheets + SQLite)
- API contracts and error handling
- Infrastructure and deployment

---

## 2. Design Principles

| Principle | Description |
|-----------|-------------|
| Sheets-first | Google Sheets is the primary database |
| Human-readable | Instructor can inspect all state manually |
| Low friction | Email + claim code, no passwords |
| Low cost | $6/month droplet |
| No lock-in | Standard Linux + Docker |
| Debuggable | Everything accessible via SSH |

---

## 3. Architecture

### 3.1 Runtime Topology

```
Browser
    │
    ▼ HTTPS :443
┌─────────────────────┐
│  Nginx (host)       │  ← TLS termination
└─────────────────────┘
    │ HTTP :8000 (localhost)
    ▼
┌─────────────────────┐
│  Docker container   │
│  ┌───────────────┐  │
│  │   FastAPI     │  │
│  └───────────────┘  │
│         │           │
│    ┌────┴────┐      │
│    ▼         ▼      │
│  SQLite   Sheets    │
└─────────────────────┘
```

### 3.2 Components

| Component | Purpose |
|-----------|---------|
| Nginx (host) | TLS termination, reverse proxy |
| Docker | Runtime isolation |
| FastAPI | Application server |
| SQLite | Magic tokens, rate limits, sessions |
| Google Sheets | Roster, quizzes, submissions |
| GitHub Actions | CI/CD pipeline |
| ForwardEmail SMTP | Magic link delivery |

---

## 4. Environment Variables

All configuration via environment variables. Secrets stored only on droplet.

### 4.1 Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (32+ chars) | `your-secret-key-here` |
| `GOOGLE_SHEETS_ID` | Spreadsheet ID from URL | `1BxiMVs0XRA5nFMdKvBd...` |
| `GOOGLE_SERVICE_ACCOUNT_PATH` | Path to service account JSON | `/etc/classapp/sa.json` |
| `SMTP_HOST` | SMTP server hostname | `smtp.forwardemail.net` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP username | `noreply@example.com` |
| `SMTP_PASS` | SMTP password | `password` |
| `BASE_URL` | Public URL (no trailing slash) | `https://class.example.com` |

### 4.2 Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `production` | `development` or `production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `SQLITE_PATH` | `/var/lib/classapp/app.db` | SQLite database path |

---

## 5. Hosting

### 5.1 DigitalOcean Droplet

| Spec | Value |
|------|-------|
| Type | Basic Droplet |
| vCPU | 1 |
| RAM | 1 GiB |
| OS | Ubuntu 24.04 LTS |
| Cost | $6/month |

**Why not App Platform**: Costs $12-17/month, ephemeral filesystem breaks SQLite, reduced debuggability.

### 5.2 Directory Structure (on droplet)

```
/opt/classapp/           # Application root
├── docker-compose.yml
└── env/
    └── .env             # Environment variables

/var/lib/classapp/       # Persistent data
└── app.db               # SQLite database

/etc/classapp/           # Secrets
└── service-account.json # Google service account
```

---

## 6. Deployment

### 6.1 One-Time Provisioning

Run once on fresh droplet:

1. Install Docker + Docker Compose
2. Install Nginx
3. Configure firewall: allow 22, 80, 443
4. Install certbot, obtain TLS certificate
5. Create directories (see 5.2)
6. Copy secrets to droplet

### 6.2 Continuous Deployment

On every push to `main`:

```
GitHub Actions
    │
    ├─► Build Docker image
    ├─► Push to GHCR
    ├─► SSH to droplet
    ├─► docker compose pull
    └─► docker compose up -d
```

Secrets never leave the droplet. GitHub Actions only triggers deployment.

---

## 7. Authentication

### 7.1 Identity Model

- Students pre-provisioned by `student_id` in Roster sheet
- Email unknown until student claims account
- Students claim by entering their `student_id` (no claim code needed)
- Email becomes permanent login identifier

### 7.2 Authentication Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Student enters email                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Magic link sent (15 min TTL)               │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  Student clicks link                     │
└─────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    ┌──────────────────┐        ┌──────────────────┐
    │ Email claimed?   │        │ Email not found  │
    │ → Create session │        │ → Show claim form│
    └──────────────────┘        └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ Enter student_id │
                                └──────────────────┘
                                          │
                                          ▼
                                ┌──────────────────┐
                                │ Bind email       │
                                │ → Onboarding     │
                                └──────────────────┘
```

### 7.3 Session Management

After successful authentication:

| Property | Value |
|----------|-------|
| Storage | HTTP-only secure cookie |
| Format | Signed JWT |
| Cookie name | `session` |
| TTL | 7 days |
| JWT payload | `{email, student_id, exp}` |

### 7.4 Security Properties

- No passwords stored
- Magic tokens: one-time use, 15 min TTL
- Student ID required for claim (must exist in Roster)
- No user enumeration (same response for known/unknown emails)
- Rate limiting: 3 requests per email per 15 minutes
- All traffic over TLS

---

## 8. Google Sheets Data Model

Single spreadsheet with these tabs (exact names required):

### 8.1 `Roster`

Primary roster. One row per student. Instructor pre-populates `student_id`, `full_name`, `program_plan`, and `student_level`. Other fields are filled by students during onboarding or via profile updates.

| Column | Type | Description |
|--------|------|-------------|
| student_id | string | Unique identifier (e.g., `10844370`) |
| full_name | string | Full name as "Last, First" (e.g., `Bhandari, Vaibhav`) |
| preferred_email | string | Student's preferred email (set during claim) |
| preferred_name | string | Display name (optional) |
| preferred_name_phonetic | string | Phonetic pronunciation (optional) |
| preferred_pronoun | string | Pronouns (optional, e.g., `he/him`) |
| linkedin | string | LinkedIn profile URL (optional) |
| program_plan | string | Academic program (pre-filled by instructor) |
| student_level | string | `Freshman`, `Sophomore`, etc. (pre-filled) |
| cs_experience | string | CS/tech experience level (optional) |
| computer_system | string | Hardware/OS description (optional) |
| hobbies | string | Personal interests (optional) |
| used_netlabs | string | `Yes`/`No` - prior Netlabs experience (optional) |
| used_tryhackme | string | `Yes`/`No` - prior TryHackMe experience (optional) |
| class_goals | string | What they want from the class (optional) |
| support_request | string | Special support needs (optional) |
| claimed_at | ISO timestamp | When account was claimed |
| onboarding_completed_at | ISO timestamp | When onboarding was completed |
| last_login_at | ISO timestamp | Most recent login |

**Constraints**:
- `student_id` must be unique
- `preferred_email` blank until claimed, then immutable
- Claim rejected if `claimed_at` is set

### 8.2 `Onboarding_Responses`

Append-only log of onboarding answers. One row per question per student.

| Column | Type | Description |
|--------|------|-------------|
| timestamp | ISO timestamp | Submission time |
| student_id | string | FK to Roster |
| email | string | Student email |
| form_version | string | Version identifier (e.g., `v1`) |
| question_key | string | Field name (e.g., `goals`) |
| question_label | string | Display text |
| answer | string | Response (semicolon-separated if multi) |
| answer_type | string | `text`, `select`, `multiselect` |
| source | string | `web` |

### 8.3 `MagicLink_Requests`

Audit log for magic link requests.

| Column | Type | Description |
|--------|------|-------------|
| requested_at | ISO timestamp | Request time |
| email | string | Requested email |
| result | string | `sent`, `rate_limited`, `error` |
| note | string | Additional context |

### 8.4 `Quizzes`

Quiz metadata. One row per quiz.

| Column | Type | Description |
|--------|------|-------------|
| quiz_id | string | Unique ID (e.g., `q001`) |
| title | string | Display title |
| content_path | string | Path to markdown file |
| open_at | ISO timestamp | When quiz opens |
| close_at | ISO timestamp | When quiz closes |
| attempts_allowed | integer | Max attempts (0 = unlimited) |
| status | string | `draft`, `published`, `archived` |
| total_points | integer | Sum of question points |

### 8.5 `Quiz_Submissions`

Append-only log of quiz attempts.

| Column | Type | Description |
|--------|------|-------------|
| submitted_at | ISO timestamp | Submission time |
| quiz_id | string | FK to Quizzes |
| attempt | integer | Attempt number (1, 2, ...) |
| student_id | string | FK to Roster |
| email | string | Student email |
| answers_json | JSON string | `{"q1": "A", "q2": ["B","C"]}` |
| score | number | Points earned |
| max_score | number | Points possible |
| autograde_json | JSON string | Per-question results |
| source | string | `web` |

### 8.6 `Schedule`

Class schedule. One row per session. Instructor updates this directly in Sheets.

| Column | Type | Description |
|--------|------|-------------|
| session | string | Session date (e.g., `1/23/2026`) |
| desc | string | Session title/description (e.g., `1 - Introduction`) |
| notes | string | Additional notes (e.g., `Quiz 1`, `Lab 2\nQuiz 2`) |
| slides_link | string | URL to slides (optional) |
| recording_link | string | URL to recording (optional) |

### 8.7 `Config`

Key-value configuration.

| Key | Example Value | Description |
|-----|---------------|-------------|
| course_title | `Security 101` | Displayed in UI |
| term | `Spring 2025` | Current term |
| magic_link_ttl_minutes | `15` | Token expiry |
| rate_limit_per_email_15m | `3` | Max requests per window |
| onboarding_form_version | `v1` | Current form version |

---

## 9. SQLite Data Model

Local SQLite for ephemeral/high-frequency data.

### 9.1 `magic_tokens`

```sql
CREATE TABLE magic_tokens (
    token_hash TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used_at TEXT,
    status TEXT DEFAULT 'pending'  -- pending, used, expired
);
CREATE INDEX idx_tokens_email ON magic_tokens(email);
```

### 9.2 `rate_limits`

```sql
CREATE TABLE rate_limits (
    key TEXT PRIMARY KEY,          -- e.g., "magic:user@example.com"
    window_start TEXT NOT NULL,
    count INTEGER DEFAULT 1
);
```

---

## 10. Onboarding

### 10.1 Form Fields

All fields are optional. Only fields that are empty in the Roster are shown during onboarding. Pre-filled fields (e.g., `program_plan`, `student_level`) are skipped.

| Field | Type | Label |
|-------|------|-------|
| preferred_name | text | Preferred Name |
| preferred_name_phonetic | text | How to pronounce your name |
| preferred_pronoun | text | Preferred Pronouns |
| linkedin | url | LinkedIn Profile URL |
| cs_experience | text | CS/Tech Experience |
| computer_system | text | What Computer System (H/W-OS) |
| hobbies | text | Hobbies |
| used_netlabs | select | Have you used Netlabs before? (Yes/No) |
| used_tryhackme | select | Have you used TryHackMe before? (Yes/No) |
| class_goals | textarea | What do you want from this class? |
| support_request | textarea | Any special support request for the teacher? |

### 10.2 On Submit

1. Update `Roster` row with submitted fields
2. Set `onboarding_completed_at` timestamp
3. Append one row per field to `Onboarding_Responses`
4. Invalidate cache for this student
5. Redirect to `/home`

---

## 11. Quiz System

### 11.1 Content Source

Quiz content stored as Markdown files:

```
content/
└── quizzes/
    ├── 001-intro.md
    ├── 002-basics.md
    └── 003-advanced.md
```

- Filename format: `NNN-slug.md`
- `quiz_id` = `q` + numeric prefix (e.g., `q001`)
- Numeric prefix defines display order

### 11.2 Quiz Markdown Format

```markdown
---
title: Introduction Quiz
---

## Q1 [mcq_single, 2pts]

What is 2 + 2?

- [ ] 3
- [x] 4
- [ ] 5

## Q2 [mcq_multi, 3pts]

Select all prime numbers:

- [x] 2
- [x] 3
- [ ] 4
- [x] 5

## Q3 [numeric, 1pt]

How many bits in a byte?

answer: 8

## Q4 [short_text, 2pts]

What command lists directory contents?

answer: ls
```

**Format rules**:
- YAML frontmatter with `title`
- Each question starts with `## Q{n}` header
- Header contains `[type, points]`
- MCQ: checkboxes with `[x]` for correct answers
- Numeric/short_text: `answer:` line with expected value

### 11.3 Question Types

| Type | Grading Logic |
|------|---------------|
| `mcq_single` | Exact match of selected option |
| `mcq_multi` | All correct selected, none incorrect |
| `numeric` | Exact integer match |
| `short_text` | Case-insensitive, trimmed match |

### 11.4 Auto-Grading Output

```json
{
  "q1": {"correct": true, "points": 2, "max": 2},
  "q2": {"correct": false, "points": 0, "max": 3, "expected": ["2","3","5"], "got": ["2","4"]},
  "q3": {"correct": true, "points": 1, "max": 1}
}
```

### 11.5 Attempt Tracking

- Count attempts from `Quiz_Submissions` sheet
- Reject submission if attempts >= `attempts_allowed`
- `attempts_allowed = 0` means unlimited

---

## 12. API Contract

### 12.1 Routes

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | no | Sign-in page |
| POST | `/auth/request-link` | no | Send magic link |
| GET | `/auth/verify` | no | Validate token, create session |
| POST | `/auth/logout` | yes | Clear session |
| GET | `/claim` | token | Claim form |
| POST | `/claim` | token | Process claim |
| GET | `/onboarding` | yes | Onboarding form |
| POST | `/onboarding` | yes | Submit onboarding |
| GET | `/home` | yes | Dashboard |
| GET | `/quizzes` | yes | Quiz list |
| GET | `/quiz/{id}` | yes | Quiz form |
| POST | `/quiz/{id}` | yes | Submit quiz |
| GET | `/me` | yes | Profile page |
| GET | `/schedule` | yes | Class schedule |
| GET | `/health` | no | Health check |

### 12.2 Health Check

`GET /health`

```json
{
  "status": "ok",
  "checks": {
    "sqlite": true,
    "sheets": true
  },
  "version": "1.0.0"
}
```

Returns `200` if healthy, `503` if degraded.

### 12.3 Error Response Format

All errors return JSON:

```json
{
  "error": "rate_limited",
  "message": "Too many requests. Try again in 10 minutes.",
  "detail": {
    "retry_after": 600
  }
}
```

| HTTP Status | Error Code | When |
|-------------|------------|------|
| 400 | `bad_request` | Invalid input |
| 401 | `unauthorized` | Missing/invalid session |
| 403 | `forbidden` | Action not allowed |
| 404 | `not_found` | Resource doesn't exist |
| 429 | `rate_limited` | Too many requests |
| 500 | `internal_error` | Server error |

---

## 13. Logging

Structured JSON logs to stdout.

### 13.1 Log Format

```json
{
  "ts": "2025-01-22T10:30:00Z",
  "level": "INFO",
  "event": "magic_link_sent",
  "email": "student@example.com",
  "request_id": "abc123"
}
```

### 13.2 Events to Log

| Event | Level | Fields |
|-------|-------|--------|
| `magic_link_sent` | INFO | email |
| `magic_link_rate_limited` | WARN | email, count |
| `claim_success` | INFO | student_id, email |
| `claim_failed` | WARN | reason |
| `login_success` | INFO | student_id |
| `quiz_submitted` | INFO | student_id, quiz_id, score |
| `sheets_error` | ERROR | operation, error |

---

## 14. Caching

In-memory cache (single process). Invalidate on writes.

| Data | TTL | Invalidate On |
|------|-----|---------------|
| Config values | 5 min | — |
| Roster by email | 2 min | claim, onboarding, profile update |
| Roster by ID | 2 min | claim, onboarding, profile update |
| Quizzes list | 5 min | — |
| Parsed quiz content | 15 min | — |
| Schedule entries | 5 min | — |
| Student submissions | 2 min | quiz submit |

---

## 15. UI

### 15.1 Screens

| Path | Screen | Description |
|------|--------|-------------|
| `/` | Sign-in | Email input form |
| `/claim` | Claim | student_id form |
| `/onboarding` | Onboarding | Multi-field form |
| `/home` | Dashboard | Welcome, quick links |
| `/quizzes` | Quiz list | Available quizzes with status |
| `/quiz/{id}` | Quiz | Questions and submit |
| `/me` | Profile | View/edit all profile fields |
| `/schedule` | Schedule | Class schedule with links |

### 15.2 Characteristics

- Server-rendered HTML (Jinja2 templates)
- Mobile-friendly (responsive CSS)
- No JavaScript framework required
- Minimal inline CSS or single stylesheet
- Flash messages for feedback

---

## 16. Nginx Configuration

```nginx
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

---

## 17. Acceptance Criteria

- [ ] 30 students can log in simultaneously
- [ ] Magic link → claim → onboarding works end-to-end
- [ ] Quizzes auto-grade correctly for all question types
- [ ] All state changes reflected in Google Sheets
- [ ] Push to `main` deploys within 5 minutes
- [ ] Health check returns accurate status
- [ ] Monthly cost remains ~$6

---

**End of Specification**
