# Project State

**Current Stage:** Stage 0 — Preparation (complete); Stage 1 — Users & Auth
(functionally covers roadmap Days 13, 14, 15, 16, and 19 — see note below)
**Current Day:** Day 15 completed (roadmap numbering); Day 16 (password reset)
and Day 19 (login history) are also already delivered in substance
**Next:** Pending Roadmap Revision — see "Unresolved decisions" below.
Deliberately not stated as "Day 16": that content already exists.
**Branch:** main
**Coverage:** <re-run `./scripts/test.sh` — Batch 1 added new tests, any
previously recorded figure here is stale>

## Note on day numbering (found during the 2026-09-21 full audit)

Per ADR-005, the Days 13–15 mini-stage delivered only what Days 5–7 hadn't
already covered. In practice this pulled in content the roadmap assigns to
Day 16 (password reset) and Day 19 (login history), while Day 15's own
literal content (login, refresh) had already shipped on Day 5 — only logout
was genuinely new on "Day 15." From here on, roadmap day numbers describe
content, not a literal session count. What to do about the numbering itself
is an open decision — see below.

## Completed

**Days 1–12 (infrastructure):**
- Day 1: repository, uv, Docker (PostgreSQL 17.11, Redis 8 — see Unresolved
  Decisions re: the documented PostgreSQL 18 target), typed settings via
  pydantic-settings
- Day 2: Ruff (lint + format), mypy strict, Bandit, pre-commit, GitHub
  Actions CI
- Day 3: pytest + pytest-django + coverage; 8 Django apps; shared abstract
  models
- Day 4: DRF with versioning prefix (`/api/v1/`), pagination, filtering;
  drf-spectacular (Swagger, ReDoc) — note: URL-prefix only, no DRF
  `DEFAULT_VERSIONING_CLASS` configured (see Unresolved Decisions)
- Day 5: Custom email-based User, JWT (rotation + blacklisting),
  IsOwnerOrReadOnly permission, `/users/me/`
- Day 6: Celery + Redis broker; async email via NotificationService
- Day 7: MinIO via django-storages; avatar upload; content-based image
  validation
- Day 8: structured logging, global exception handler, RequestID +
  RequestLogging middleware — confirmed during the audit to be genuinely
  complete, delivered alongside Day 6's session rather than as its own
- Day 9: CORS; security headers; rate limiting (7 throttle scopes);
  SECRET_KEY min length; JWT_SIGNING_KEY option; `check --deploy` in CI
- Day 11: full README; `docs/ARCHITECTURE.md` with Mermaid diagrams —
  confirmed during the audit to need a refresh (see Group B below), not a
  rewrite
- Day 12: audit performed

**Days 13–15 (auth mini-stage; functionally includes Day 16 and Day 19
content — see note above):**
- Self-registration with password validation
- Email verification (dedicated token generator + resend endpoint)
- `LoginEvent` model and login history endpoint (Day 19 content)
- Password reset with JWT invalidation (Day 16 content)
- Logout via refresh token blacklisting

**Batch 1 — confirmed, roadmap-independent fixes (2026-09-21, applied
during the full audit, tests passing):**
- `custom_exception_handler` now recovers the real message for DRF's
  dict-with-`detail` case, single-item `non_field_errors`, and single-item
  validation-error lists; field-level errors still land in `details`
  unchanged
- Password-reset password-change + token-blacklist now run inside a single
  `transaction.atomic()`
- `blacklist_all_tokens_for` uses `bulk_create(ignore_conflicts=True)`
  instead of a per-token `get_or_create` loop
- `apps/common/tests/test_middleware.py` now exercises the real
  `/api/v1/health/` path and asserts `200 OK`
- New: `apps/users/tests/test_services.py` (direct coverage of
  `blacklist_all_tokens_for`, including a query-count regression test).
  Strengthened: message-content assertions added to
  `test_password_reset.py`, `test_verification.py`, `test_logout.py`; new
  atomicity-rollback test in `test_password_reset.py`

## Deferred / Backlog

**Day 10 — Optimization: intentionally deferred, not closed.** See
`DECISIONS.md` ADR-004 (updated 2026-09-21) for the concrete map — Catalog
indexes (Day 34), Catalog caching (Day 37), Cart/Order optimization (their
own stages), production DB connection strategy (production-infrastructure
stage, blocked on the WSGI vs. ASGI decision).

**Group A — confirmed, roadmap-independent, not yet scheduled (candidates
for a further batch, no architecture decisions needed):**
- `delete_old_avatar_on_change`: skip the extra `SELECT` when the avatar
  hasn't actually changed (narrow fix only — moving the file deletion
  itself into a service, to close the save-order race, is Group B, tied to
  service-layer consolidation)
- Avatar upload: reject oversized uploads via `Content-Length` before
  reading the body (narrow fix only — the full fix needs a reverse proxy,
  Group B / Day 76)
- `X-Request-ID`: validate or length-limit the client-supplied value before
  it reaches the logs
- Throttle scopes: single shared source for the scope strings instead of
  duplicating them between settings and each view
- Test gaps: `ResendVerificationEmailView` has no coverage at all; the
  email-enumeration test doesn't compare known vs. unknown email; neither
  password-reset nor verify-email tests a malformed `uid`; no test exercises
  the real link from `mail.outbox[0].body` end-to-end
- Documentation-only, no code risk: fix the documented `DJANGO_DEBUG`
  default (README says `True`, code default is `False`); add `EMAIL_*`
  variables to the README environment-variable table; add
  `/auth/token/verify/` to the documented endpoint list

**Group B — architecture/roadmap-dependent, no code changes until Roadmap
Revision:**
- Service-layer consolidation: registration/verification/password-reset/
  logout mutation logic is split inconsistently between serializers,
  views, and `apps/users/services.py`
- Duplicated uid-decode logic between `PasswordResetConfirmSerializer` and
  `VerifyEmailSerializer`
- `users`-domain routes split between `config/urls_v1.py` and
  `apps/users/urls.py`
- API versioning: URL prefix only today, no `DEFAULT_VERSIONING_CLASS`
- PostgreSQL 17.11 (actual) vs. PostgreSQL 18 (documented intent) — see
  Unresolved Decisions
- `docs/ARCHITECTURE.md` ER diagram is stale (missing `LoginEvent`, missing
  `User.is_verified`); a few smaller diagram-precision notes (`AuthN` drawn
  as if it were Django middleware; a `Worker → Storage` arrow with no
  matching task yet; `IsAdminUser` described as an applied pattern though
  nothing uses it yet)

## Unresolved decisions (need your input before the corresponding stage)

1. PostgreSQL 17.11 (docker-compose.yml, CI) vs. PostgreSQL 18 (README,
   `02_Project.md`, `ARCHITECTURE.md`) — both are real, current, supported
   versions. Was 17.11 deliberate? Standardize before pgvector data exists
   (AI stage, Day 59+) — migrating the DB version after is far more
   expensive than before.
2. `docker/` — referenced in README and `pyproject.toml`'s mypy config but
   empty in `project_dump.txt`. Confirm whether it's simply not populated
   yet.
3. Stage 1's remaining literal scope (Day 17 — phone/bio on the profile;
   Day 18 — formal `AdminPermission`/`OwnerPermission` classes) — finish
   literally, or close Stage 1 by functionality with a new ADR (numbering
   below).
4. Timing for moving `users`-domain routes into `apps/users/urls.py` —
   before Catalog starts, or acceptable to defer?
5. Timing for service-layer consolidation — same question; the audit's
   recommendation is before Catalog, final call is yours.
6. API versioning strategy — URL-prefix-only indefinitely, or add
   `DEFAULT_VERSIONING_CLASS` ahead of actual need?
7. Project naming/branding ("food" vs "grocery") — likely worth deciding
   together with Roadmap Revision, given the expanded final goal.
8. Two candidate ADRs considered but not drafted this round (documenting
   `AbstractBaseUser`+`PermissionsMixin` — already recorded in
   `03_Roadmap.md` Day 13, so duplicating it into `DECISIONS.md` is
   optional; the custom request-ID/logging middleware vs. an off-the-shelf
   package) — write them now, or fold into Roadmap Revision prep?

## Known issues

- `project_dump.txt` being committed vs. gitignored — not verified either
  way during this audit; worth a quick check.
- The two items previously listed here (`db.sqlite3`, a stray
  `test_enviroment.cpython-*.pyc`) do not appear anywhere in the audited
  `project_dump.txt` — not even as skipped binaries, unlike files that
  really are present (e.g. `.coverage`) — strong evidence both are already
  gone. Removed from this list; re-add if either resurfaces.
- `coverage fail_under = 40` vs. the 90% ADR-001 target — already
  reconciled: `pyproject.toml` carries an inline comment explaining the
  floor-vs-target distinction. Not an open issue.

## Context for a new chat

Upload together with:
- This file
- `DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `01_System.md`, `02_Project.md`, `03_Roadmap.md`, `04_Constitution.md`,
  `05_Development_standards.md`
- A fresh `project_dump.txt`
