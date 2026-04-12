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
- **`uv.lock`** — pinned versions for reproducible installs (commit this file).

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

## Run the API

From the **backend** directory so imports resolve correctly:

```bash
cd backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Health: `GET http://localhost:8000/`
- OpenAPI docs: `http://localhost:8000/docs`

Main routes include:

- `POST /api/v1/register` — create user
- `POST /api/v1/login` — lookup user by email
- `POST /api/v1/generate-pathway` — full pipeline
- `GET /api/v1/history/{user_id}` — past pathways
- `GET /api/v1/roles` — allowed target roles

## Run the frontend

By default the UI calls `http://localhost:8000`. In deployment, set **`RBPLPE_API_URL`** to your public API origin (no trailing slash), or define the same key in **Streamlit secrets** (e.g. Streamlit Community Cloud).

```bash
uv run streamlit run frontend/app.py
```

## Deploy

You are shipping **two Python apps** (API + Streamlit) and two data stores (**PostgreSQL**, **Neo4j**). Point both apps at the same databases via environment variables.

### 1. Provision services

- **PostgreSQL** — create a database; set `DATABASE_URL` to a URL the API host can reach (TLS URLs for managed providers are fine if the driver supports them).
- **Neo4j** — Aura or self-hosted Bolt endpoint; set `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
- **API host** — needs **enough RAM** for PyTorch + transformers (JobBERT warms up at startup). Start with **one** `uvicorn` worker so the model is not duplicated across processes.

### 2. API (FastAPI)

On a VM or container:

```bash
uv sync
cd backend
# Set DATABASE_URL, NEO4J_* in the environment or a .env file next to where Python loads it
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Put **HTTPS** and routing in front with **nginx**, **Caddy**, or your platform’s load balancer. For production, run without `--reload`.

Ensure **`data/cleaned/`** and **`models/ppo_agent`** (if you use PPO) exist on the API machine at paths your `ml/` code resolves (run from `backend/` as in development, or adjust paths / working directory accordingly).

### 3. Frontend (Streamlit)

Run Streamlit where users reach it (second VM, or Streamlit Community Cloud, etc.). Configure the API URL:

| Where | How |
|--------|-----|
| Shell / Docker | `export RBPLPE_API_URL=https://api.yourdomain.com` |
| Streamlit Cloud | App secrets: `RBPLPE_API_URL` = `https://api.yourdomain.com` |

```bash
RBPLPE_API_URL=https://api.yourdomain.com uv run streamlit run frontend/app.py --server.address 0.0.0.0 --server.port 8501
```

The UI talks to the API with **server-side** `requests`, so you do not need browser CORS for this Streamlit app alone.

### 4. Platforms (high level)

- **Docker** — one image for the API and one for Streamlit (or a single image with two commands); copy the repo, `uv sync`, set env vars, expose ports 8000 / 8501.
- **Railway / Render / Fly.io** — deploy the API as a web service with the same start command; attach managed Postgres if offered; run Neo4j separately (e.g. Aura) or as another service.
- **Streamlit Community Cloud** — connect the GitHub repo, set secrets for `RBPLPE_API_URL`, ensure the API is reachable on the public internet with TLS.

### 5. Checklist

- [ ] `DATABASE_URL` and Neo4j variables set on the API
- [ ] API health: `GET /`
- [ ] `RBPLPE_API_URL` (or Streamlit secret) points to that API
- [ ] Neo4j graph populated for your roles
- [ ] Course CSV and optional PPO artifacts present on the API host

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

(Add `pytest` and convert to pytest style if you want a single `pytest` entry point.)


