# classapp – development workflow
# Usage: make <target>

# ── Config ────────────────────────────────────────────────────────────────────
VM_IP       := $(shell grep ^VM_IP .env | cut -d= -f2)
VM_PASSWORD := $(shell grep ^VM_PASSWORD .env | cut -d= -f2)
SERVER_DIR  := /opt/classapp
SERVER_ENV  := $(SERVER_DIR)/env/.env
PROD_URL    := https://classapp.cyberdefendersprogram.com
PYTHON      := .venv/bin/python
PYTEST      := .venv/bin/pytest
UVICORN     := .venv/bin/uvicorn
RUFF        := .venv/bin/ruff
SSH_CMD     := sshpass -p '$(VM_PASSWORD)' ssh -o StrictHostKeyChecking=no root@$(VM_IP)

.PHONY: help dev docker-dev test lint fmt seed seed-cis60 seed-cis52 seed-cis52-dev \
        seed-meta seed-cis52-prod \
        deploy logs ssh health restart db-reset prod-status prod-switch-class

# ── Default ───────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  make dev          Run app locally with hot-reload"
	@echo "  make docker-dev   Run app locally in Docker"
	@echo ""
	@echo "  make test         Run test suite"
	@echo "  make lint         Check code style (ruff)"
	@echo "  make fmt          Auto-format code (ruff)"
	@echo ""
	@echo "  make deploy       Push to main → CI builds image → server auto-deploys"
	@echo "  make logs         Tail live server logs"
	@echo "  make ssh          Open shell on server"
	@echo "  make health       Check server health endpoint"
	@echo "  make restart      Restart containers on server"
	@echo "  make db-reset     Wipe SQLite on server (resets sessions/cache)"
	@echo ""
	@echo "  make prod-status                              Show active class + health on the server"
	@echo "  make prod-switch-class COURSE=x SHEETS_ID=y   Point server at a class's sheet + reset DB"
	@echo "                                                 (deliberate — NOT run by 'make deploy' / git push)"
	@echo ""
	@echo "  make seed           Seed active sheet structure"
	@echo "  make seed-cis60     Seed CIS 60 sheet structure"
	@echo "  make seed-cis52     Seed CIS 52 sheet structure + course data"
	@echo "  make seed-cis52-dev Seed CIS 52 structure + data + dev test roster row (10110234)"
	@echo ""
	@echo "  make seed-meta COURSE=x SHEETS_ID=y   Copy Config + Quizzes metadata onto any sheet"
	@echo "                                         (not Schedule/Roster — safe for hand-curated sheets)"
	@echo "  make seed-cis52-prod                  Shortcut: seed-meta for the CIS52 production sheet"
	@echo ""

# ── Local dev ─────────────────────────────────────────────────────────────────
dev:
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

docker-dev:
	docker compose -f docker-compose.dev.yml up --build

# ── Testing & linting ─────────────────────────────────────────────────────────
test:
	$(PYTEST) tests/ -q

test-v:
	$(PYTEST) tests/ -v

lint:
	$(RUFF) check app/ tests/
	$(RUFF) format --check app/ tests/

fmt:
	$(RUFF) format app/ tests/
	$(RUFF) check --fix app/ tests/

# ── Seeding ───────────────────────────────────────────────────────────────────
seed:
	GOOGLE_SERVICE_ACCOUNT_PATH=.secrets/service-account.json \
	$(PYTHON) scripts/seed_sheets.py --create-structure

seed-cis60:
	GOOGLE_SHEETS_ID=1Q9CF-4b5YkvIjbyOP0Q9dzb-4KetfLUfd_PqFmvDyfA \
	GOOGLE_SERVICE_ACCOUNT_PATH=.secrets/service-account.json \
	$(PYTHON) scripts/seed_sheets.py --create-structure

seed-cis52:
	GOOGLE_SHEETS_ID=1CfD099p5A6h7YMxqsjsr4vEuqZjRIyhQKTIAaKGeJDI \
	GOOGLE_SERVICE_ACCOUNT_PATH=.secrets/service-account.json \
	$(PYTHON) scripts/seed_sheets.py --course cis52 --all

# Dev-only: also drops in an unclaimed test roster row (student_id 10110234)
# so /claim + /onboarding + the intro quiz can be exercised locally.
seed-cis52-dev:
	GOOGLE_SHEETS_ID=1CfD099p5A6h7YMxqsjsr4vEuqZjRIyhQKTIAaKGeJDI \
	GOOGLE_SERVICE_ACCOUNT_PATH=.secrets/service-account.json \
	$(PYTHON) scripts/seed_sheets.py --course cis52 --all --seed-test-roster

# Reusable across courses/sheets: copies Config + Quizzes metadata only (not
# Schedule, Book_Reading, or Roster) onto any sheet — safe to run against a
# hand-curated sheet like production, since it only adds missing Config keys
# and Quizzes rows, never touches existing ones or duplicates Schedule dates.
seed-meta:
	@if [ -z "$(COURSE)" ] || [ -z "$(SHEETS_ID)" ]; then \
		echo "Usage: make seed-meta COURSE=cis52 SHEETS_ID=<google-sheet-id>"; \
		exit 1; \
	fi
	GOOGLE_SHEETS_ID=$(SHEETS_ID) \
	GOOGLE_SERVICE_ACCOUNT_PATH=.secrets/service-account.json \
	$(PYTHON) scripts/seed_sheets.py --course $(COURSE) --seed-meta

seed-cis52-prod:
	@$(MAKE) seed-meta COURSE=cis52 SHEETS_ID=1mBWKLwaoGDp0rxKcOSrdqxZX7CbZv0bCi-EIk74alY4

# ── Server ────────────────────────────────────────────────────────────────────
# deploy = git push → GitHub Actions builds + pushes image → SSHs to server
deploy:
	git push origin main
	@echo ""
	@echo "  CI is building and deploying. Watch progress at:"
	@echo "  https://github.com/$(shell git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
	@echo ""

logs:
	$(SSH_CMD) "cd $(SERVER_DIR) && docker compose logs -f --tail=50"

ssh:
	sshpass -p '$(VM_PASSWORD)' ssh -o StrictHostKeyChecking=no root@$(VM_IP)

health:
	@curl -s $(PROD_URL)/health | $(PYTHON) -m json.tool

restart:
	$(SSH_CMD) "cd $(SERVER_DIR) && docker compose restart"
	@echo "Restarted."

db-reset:
	@echo "Wiping SQLite on server (sessions + cache)..."
	$(SSH_CMD) "docker exec \$$(docker ps --format '{{.Names}}' | grep classapp) rm -f /app/data/app.db && docker compose -f $(SERVER_DIR)/docker-compose.yml restart"
	@echo "Done. DB will reinitialize on next request."

# ── Production class switch ──────────────────────────────────────────────────
# Deliberate, explicit action — NOT triggered by 'make deploy' / git push, since
# it changes which sheet is live and resets all session/cache state. Run this
# only when actually cutting the server over to a class.
prod-status:
	@echo "Active class on server:"
	@$(SSH_CMD) "grep -E '^(GOOGLE_SHEETS_ID|ACTIVE_CLASS|ENV)=' $(SERVER_ENV)"
	@echo ""
	@$(MAKE) health

prod-switch-class:
	@if [ -z "$(COURSE)" ] || [ -z "$(SHEETS_ID)" ]; then \
		echo "Usage: make prod-switch-class COURSE=cis52 SHEETS_ID=<google-sheet-id>"; \
		exit 1; \
	fi
	@echo "Switching production to '$(COURSE)' (sheet $(SHEETS_ID))..."
	@echo "  1/2 Updating server env (GOOGLE_SHEETS_ID, ACTIVE_CLASS)..."
	$(SSH_CMD) "sed -i -E 's|^GOOGLE_SHEETS_ID=.*|GOOGLE_SHEETS_ID=$(SHEETS_ID)|' $(SERVER_ENV) && \
		if grep -q '^ACTIVE_CLASS=' $(SERVER_ENV); then \
			sed -i -E 's|^ACTIVE_CLASS=.*|ACTIVE_CLASS=$(COURSE)|' $(SERVER_ENV); \
		else \
			echo 'ACTIVE_CLASS=$(COURSE)' >> $(SERVER_ENV); \
		fi"
	@echo "  2/2 Recreating container (picks up new env; also resets the"
	@echo "      container-local SQLite DB, which isn't on a mounted volume)..."
	$(SSH_CMD) "cd $(SERVER_DIR) && docker compose up -d --force-recreate"
	@echo ""
	@echo "Waiting for the app to come back up..."
	@sleep 6
	@$(MAKE) prod-status
