# RB-PLPE

**Role-Based Personalised Learning Pathway Engine** — a system that takes a learner’s skills, a target job role, and constraints, then proposes an ordered learning pathway backed by a small ML stack (skill normalization, knowledge-graph requirements, gap scoring, and optional PPO-based course ordering).

## What it does

1. **Register / log in** users (PostgreSQL).
2. **Normalize skills** from free text using JobBERT-style extraction (`ml/skill_extractor.py`).
3. **Load role requirements** from **Neo4j** (`ml/knowledge_graph.py`).
4. **Compute skill gaps** (`ml/gap_analysis.py`).
5. **Generate a course pathway** with a **PPO** agent when a trained model is present, with rule-based fallback (`ml/pathway_generator.py`).

The **FastAPI** app exposes JSON APIs; the **Streamlit** UI calls those APIs.

## Dependency management (uv)

This project uses **[uv](https://docs.astral.sh/uv/)** for Python environments and dependencies:

- **`pyproject.toml`** — project metadata and dependency ranges.
- **`uv.lock`** — pinned versions for reproducible installs.

Install [uv](https://github.com/astral-sh/uv#installation), then from the repo root run **`uv sync`**. That creates or updates a local **`.venv`** and installs exactly what the lockfile specifies. Use **`uv run <command>`** anywhere in this README so commands use that environment without activating the venv manually.

To add or upgrade a library later: `uv add <package>` (updates the lockfile). To refresh the lock after editing `pyproject.toml` by hand: `uv lock` then `uv sync`.

## Requirements

- **Python** `3.10.11` (see `.python-version` and `pyproject.toml`)
- **PostgreSQL** — app metadata, users, inputs, saved pathways
- **Neo4j** — role ↔ skill graph (must be populated to match your target roles)
- **Disk / RAM** — first run downloads transformer weights for skill extraction (JobBERT warmup on API startup)

## Environment variables

Create a `.env` in the project root (loaded by `backend/database.py`). Sensible defaults exist for local development:

| Variable | Purpose | Default (if unset) |
|----------|---------|---------------------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://postgres:password@localhost:5432/rbplpe_database` |
| `NEO4J_URI` | Bolt URI | `bolt://127.0.0.1:7687` |
| `NEO4J_USER` | Neo4j user | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | `password` |

## Install

```bash
cd RB-PLPE
uv sync
```

This is the only install step you need for Python dependencies when using uv.



Main routes include:

- `POST /api/v1/register` — create user
- `POST /api/v1/login` — lookup user by email
- `POST /api/v1/generate-pathway` — full pipeline
- `GET /api/v1/history/{user_id}` — past pathways
- `GET /api/v1/roles` — allowed target roles



## Project layout

| Path | Role |
|------|------|
| `backend/` | FastAPI app (`main.py`), SQLAlchemy models, Pydantic schemas, DB/Neo4j wiring |
| `ml/` | Skill extraction, Neo4j queries, gap analysis, pathway generator (Gymnasium + Stable-Baselines3 PPO) |
| `frontend/` | Streamlit UI |
| `data/cleaned/` | CSV inputs (e.g. courses, role–skill mappings) used by notebooks / ML |
| `notebooks/` | Data cleaning and PPO training experiments |
| `tests/` | Scripts and checks around ML components |

## PPO model

`ml/pathway_generator.py` looks for a trained agent under `models/ppo_agent` (relative to that module’s working directory when the API runs from `backend/`). If you do not have that artifact yet, train or export it using your `notebooks/ppo_training.ipynb` workflow and place the files where the generator expects them, or rely on the rule-based path in code where applicable.

## Tests

The `tests/` folder contains runnable Python scripts (e.g. skill extractor cases, pathway comparisons). Run them with the interpreter that has project dependencies installed, for example:

```bash
uv run python tests/test_skill_extractor.py
```



