# Project State

**Current Stage:** Stage 0 — Preparation (effectively complete)
**Current Day:** Day 15 completed
**Next Day:** Day 16 (after audit)
**Branch:** main
**Coverage:** <вставь актуальный процент из `./scripts/test.sh`>

## Completed

**Days 1–12 (infrastructure):**
- Day 1: repository, uv, Docker (PostgreSQL 18, Redis 8), typed settings via pydantic-settings
- Day 2: Ruff (lint + format), mypy strict, Bandit, pre-commit, GitHub Actions CI
- Day 3: pytest + pytest-django + coverage; 8 Django apps; shared abstract models
- Day 4: DRF with versioning (/api/v1/), pagination, filtering; drf-spectacular (Swagger, ReDoc)
- Day 5: Custom email-based User, JWT (rotation + blacklisting), IsOwnerOrReadOnly permission, /users/me/
- Day 6: Celery + Redis broker; async email via NotificationService; structured logging; global exception handler; RequestID + RequestLogging middleware
- Day 7: MinIO via django-storages; avatar upload; content-based image validation
- Day 8: (was covered alongside Day 6 in practice — verify against roadmap)
- Day 9: CORS; security headers; rate limiting (anon/user/login scopes); SECRET_KEY min length; JWT_SIGNING_KEY option; check --deploy in CI
- Day 11: full README; docs/ARCHITECTURE.md with Mermaid system + ER diagrams
- Day 12: audit

**Days 13–15 (auth mini-stage):**
- Self-registration with password validation
- Email verification (dedicated token generator + resend endpoint)
- LoginEvent model and login history endpoint
- Password reset with JWT invalidation
- Logout via refresh token blacklisting

## Deferred / Backlog

- **Day 10 — Optimization (indexes, Redis cache, API optimization).**
  Not performed. Reason: too little application code to optimize
  meaningfully; only `User` has meaningful query patterns, and its key
  lookup is already covered by a unique index. Return when
  `Catalog`/`Cart`/`Order` models exist with real query patterns.
  See `DECISIONS.md` ADR-004.

## Known issues / to verify during audit

- Root `db.sqlite3` (0 bytes) — leftover from Day 1; project uses
  PostgreSQL. Safe to delete.
- `tests/__pycache__/test_enviroment.cpython-312-pytest-9.1.1.pyc` —
  leftover from a typo file (`test_enviroment.py` →
  `test_environment.py`). The `.py` was renamed; the `.pyc` remains.
- `project_dump.txt` — should be gitignored, not committed.
- `README.md` — title says "Groery E-Commerce Backend" while
  `pyproject.toml` declares `food-ecommerce-backend`. Naming
  inconsistent. Verify which is intended.
- `DECISIONS.md` — ADR-004 and ADR-005 were missing; restored from chat
  history. Verify content matches what was actually done.
- `coverage fail_under = 40` (anti-regression floor) coexists with the
  ADR-001 target of 90% (aspirational). Distinction is intentional but
  not documented in `DECISIONS.md`.
- Some code was manually modified by the developer when the AI-proposed
  version did not run. Not all changes were reported back.
  `project_dump.txt` is the source of truth, not the AI's memory of
  prior sessions.

## Context for a new chat

Upload together with:
- This file
- `DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `01_System.md`, `02_Project.md`, `03_Roadmap.md`, `04_Constitution.md`,
  `05_Development_standards.md`
- A fresh `project_dump.txt`

## Audit in progress

- Step 1 (inventory): ✅ done
- Step 2 (roadmap reconciliation): ✅ done
- Step 3 (config coherence): ✅ done
- Step 4 (bugs, architecture, tests, security): 🔄 in progress
- Steps 5–8: pending
