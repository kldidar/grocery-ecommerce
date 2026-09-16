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

---

---

## ADR-005 — Stage 1 scope reduced to genuinely missing features

**Date:** 2026-09-XX (день, когда было принято)
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
is not authoritative; the definition of "missing" is what matters.
