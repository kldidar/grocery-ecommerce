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
