# Architecture Decision Records

This file records significant architectural decisions made during the
project, in the order they were made. Each entry captures the context
that motivated the decision, the decision itself, the alternative(s)
considered, and its consequences — per Constitution, Rule 17: an accepted
decision is not revisited without a documented reason.

---

## ADR-001 — Revision of plan duration and target coverage

**Date:** 2026-08-28
**Status:** Accepted

**Context:** `01_System.md`/`02_Project.md` fix 70 days (~210 sessions), coverage ≥85%. `03_Roadmap.md`, upon detailed elaboration, revises these numbers.

**Decision:** 80 days / 240 working sessions, target coverage — 90% (per Definition of Done for Stage 5, Day 80).

**Alternative:** Keep the original 70/210/85%, cutting functionality to meet the date — rejected: contradicts the "Production First" principle and the quality of AI modules (Days 59–70).

**Consequences:** The roadmap has already been written for the new figures.

---

## ADR-002 — Dependency and environment management via uv

**Date:** 2026-08-28
**Status:** Accepted

**Context:** The initial Day 1 implementation used `python -m venv` and `pip` with `requirements/*.txt` files. A direct instruction was received to switch to `uv` (Astral) as the single tool for dependency management, virtual environments, and Python version control.

**Decision:** `requirements/*.txt` are replaced with `pyproject.toml` (metadata and direct dependencies) and `uv.lock` (locked dependency tree).

**Alternative:** Keep pip/requirements — rejected by direct instruction; it is also objectively inferior in dependency resolution speed and build reproducibility.

**Consequences:** `uv.lock` must be committed alongside `pyproject.toml`. All commands are run via `uv run`.

---

## ADR-003 — Ruff replaces Black and isort

**Date:** 2026-08-29
**Status:** Accepted

**Context:** `01_System.md`, `02_Project.md`, and `03_Roadmap.md` list Ruff, Black, isort, mypy, and Bandit as five separate tools for Day 2. Starting with version 0.0.289, Ruff includes its own formatter (`ruff format`), compatible with Black, and the rule category `I` (import sorting), equivalent to isort.

**Decision:** Formatting and import sorting are performed via `ruff format` and rule `I`. Black and isort are not installed as separate packages.

**Alternative:** Three separate tools (Ruff linter + Black formatter + isort) — rejected: risk of formatting rule divergence between linter and formatter, slower pre-commit and CI without benefit in outcome.

**Consequences:** The entries "Black" and "isort" in the original documents are interpreted as "formatting" and "import sorting" in essence.

---

## ADR-004 — Day 10 (Optimization) postponed; Day 11 performed first

**Date:** 2026-09-05
**Status:** Accepted

**Context:** The roadmap prescribes a strict order: Day 10 (DB indexes,
Redis cache, API optimization) before Day 11 (documentation). A direct
instruction was received to proceed to Day 11.

**Additional rationale (not merely "per instruction" — `02_Project.md`
requires an objective technical reason for deviating from the order):**
Day 10 optimization today would be largely speculative. The only model
with meaningful queries is `User` (email lookup, already covered by the
implicit unique index from `unique=True`); `Catalog`/`Order`/`Cart` —
models that would give indexes and caching real substance — do not exist
yet. Documentation (Day 11), by contrast, has no technical dependency on
Day 10 and describes an already-existing system, not a hypothetical
future one.

**Decision:** Day 10 is postponed, not cancelled or removed from the
roadmap. Return to it is expected after `catalog`/`cart`/`orders` models
appear with real query patterns.

**Alternative:** Insist on the literal order — rejected: preserving
order for its own sake when an objective reason for deviation exists
would contradict the very principle that introduced this requirement in
`02_Project.md`.

**Consequences:** "Day N" numbering continues to follow the roadmap
(next after Day 11 — Day 12), with the understanding that Day 10 remains
an outstanding item in the queue, not a forgotten one.

**Update (2026-09-21, full project audit):** `LoginEvent` (migration
`0005`, generated 2026-09-09) was added after this ADR was written, so
"the only model with meaningful queries is User" is no longer accurate —
`LoginEvent` also has a real query pattern (`user.login_events.all()`,
ordered by `-created_at`). This does not change the decision: a composite
`(user_id, created_at)` index for that pattern is technically ready to
add but has no measurable benefit at the current data volume, so it
stays deferred by the same reasoning as the rest of Day 10.

Concrete map, replacing the open-ended "return to it" phrasing above:
- Redis/throttling infrastructure — already implemented and load-bearing
  today (DRF throttle classes), not a future item.
- `User`/`LoginEvent` access patterns — reviewed (see above); no action
  needed at current scale.
- Catalog indexes — Day 34.
- Catalog caching — Day 37.
- Cart/Order optimization — their own stages (around Day 55).
- Production database connection strategy (persistent connections vs.
  external pooling) — production-infrastructure stage; blocked on the
  still-undecided WSGI vs. ASGI choice.
- Anything else — only after real query patterns and measurements exist
  for the domain in question (`measure → identify bottleneck → optimize
  → measure again`).

Day 10 remains **intentionally deferred, not closed.**

---

## ADR-005 — Stage 1 scope reduced to genuinely missing features

**Date:** 2026-09-09 (inferred from migration `0005_loginevent`'s
generation timestamp — the last schema change belonging to this
mini-stage; correct if you recall the actual date differently)
**Status:** Accepted

**Context:** Stage 1 of the roadmap was planned as a full pass over
auth-related functionality (custom user, JWT, permissions, registration,
email verification, password reset, logout, login history). By the time
Stage 1 was reached, Days 5–7 had already delivered the custom user
model, JWT with rotation/blacklisting, permission classes, and a
`/users/me/` endpoint. Rebuilding these would duplicate completed,
tested work.

**Decision:** Stage 1 delivers only the genuinely missing pieces on top
of what Days 5–7 already provide: self-registration, email verification,
login history, password reset with JWT invalidation, and logout via
refresh-token blacklisting. Existing auth infrastructure is reused, not
rewritten.

**Alternative:** Follow the original Stage 1 scope literally, rebuilding
custom user and JWT — rejected: violates DRY, wastes sessions, and would
risk regressing already-working, tested functionality.

**Consequences:** Stage 1 completes earlier than originally scoped.
Freed sessions go to later stages. The roadmap's day count for Stage 1
is not authoritative; the definition of "missing" is what matters. This
also means roadmap Days 16 and 19 (password reset, login history) were
delivered inside this mini-stage rather than as their own separate
sessions — see `PROJECT_STATE.md`.

---

## ADR-006 — MAILERS over EMAIL_BACKEND (Django 6.1)

**Date:** 2026-09-21
**Status:** Accepted

**Context:** Django 6.1 introduced a `MAILERS` setting — a named-dict
configuration for one or more email backends, following the same pattern
already used by `CACHES`, `DATABASES`, `STORAGES`, and `TASKS` —
replacing the single `EMAIL_BACKEND` setting and the flat `EMAIL_*`
settings, both deprecated as of 6.1 and scheduled for removal.
`config/settings/base.py` and `production.py` already configure
`MAILERS["default"]`, and `apps/notifications/tasks.py`'s use of
`django.core.mail.send_mail()` resolves through `mailers.default`
automatically once `MAILERS` is defined. This choice was made early in
the project but never recorded, which made it indistinguishable from an
oversight on review.

**Decision:** Use `MAILERS` exclusively going forward; never fall back
to `EMAIL_BACKEND` or the flat `EMAIL_*` settings.

**Alternative:** Keep `EMAIL_BACKEND` — rejected: deprecated in the
exact Django version this project targets (`django~=6.1`) and scheduled
for removal.

**Consequences:** Any third-party package that reads
`settings.EMAIL_BACKEND` directly (rather than through Django's own
mail-sending functions) will raise `AttributeError` once `MAILERS` is
defined. Verify `MAILERS` compatibility before adding any such
dependency (Constitution Rule 22).

---

## ADR-007 — Single error response shape across the API

**Date:** 2026-09-21
**Status:** Accepted

**Context:** `apps/common/exceptions.py`'s `custom_exception_handler`
normalizes every DRF error response to
`{"error": {"code", "message", "details"}}`. Already used across the current API implementation across the whole API and documented in `README.md`, but never recorded
as a deliberate decision compared against alternatives.

**Decision:** Every error response uses
`{"error": {"code": str, "message": str, "details": object | null}}` —
`code` a stable, machine-readable identifier (`_STATUS_CODE_LABELS`),
`message` a single human-readable string, `details` an optional
structured payload (e.g. per-field validation errors).

**Alternative:** DRF's own default shape (a bare `{"detail": ...}`, or a
bare field-error dict) — rejected: the shape differs by error type
(dict vs. list vs. string), which makes client-side error handling
harder — exactly the class of bug found and fixed in Batch 1
(2026-09-21) inside this same handler. RFC 7807 Problem Details —
rejected as unnecessary ceremony for an API with a single client
(FastKart) that has no need for `type`/`instance` URIs.

**Consequences:** Any new exception type must produce a `response.data`
shape the handler already recognizes (dict with `"detail"`, dict with a
single-item `non_field_errors`-style key, list of one item, or a general
dict/list of field errors) or extend the handler explicitly — see
Batch 1 for the precedent.

---

## ADR-008 — UUID primary keys via UUIDMixin

**Date:** 2026-09-21
**Status:** Accepted

**Context:** Every concrete model inherits `UUIDMixin` (directly or via
`BaseModel`), giving it a UUID primary key instead of Django's default
auto-incrementing integer. At the same time, every app's
`AppConfig.default_auto_field` and the project-wide `DEFAULT_AUTO_FIELD`
in `config/settings/base.py` are both `BigAutoField` — meaning that
project-wide default is never actually used by any model defined in this
codebase today, which reads as an inconsistency without this record.

**Decision:** All first-party models use UUID primary keys via
`UUIDMixin`/`BaseModel`. `DEFAULT_AUTO_FIELD` stays `BigAutoField` as the
Django-recommended default for any model that does not explicitly opt
into `UUIDMixin` — in particular, models added by future third-party
packages, which Django creates using this project-wide default.

**Alternative:** Django's default auto-incrementing integer PK —
rejected: sequential IDs are guessable and leak information through the
API, URLs, and logs (e.g. total user/order count, creation ordering);
UUIDs avoid this and simplify client-generated IDs and any future
multi-region data-merge scenario.

**Consequences:** Slightly larger index/storage footprint than integer
PKs — accepted, not significant at this project's scale. Any future
third-party app's models default to `BigAutoField` unless explicitly
given a UUID PK; this is intended behavior, not an inconsistency to fix.
