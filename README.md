# RB-PLPE — Role-Based Personalised Learning Pathway Engine

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?logo=streamlit)
![Neo4j](https://img.shields.io/badge/Neo4j-5.x-blue?logo=neo4j)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![License](https://img.shields.io/badge/License-Academic-orange)

**An intelligent, end-to-end learning pathway recommendation system that identifies your skill gap and generates a personalised, optimally sequenced course roadmap for your target IT job role.**

*UPES — School of Computer Science | MCA Data Science | 2024–2026*

</div>

---

## 👥 Team

| Name | Enrollment |
|------|-----------|
| Hamant Jagwan | 590010133 |
| Tanuj Sanwal | 590010145 |
| Pawan Singh Rajwar | 590017545 |

**Internal Mentor:** Dr. Pavinder Yadav — UPES
**External Mentor:** Deborah T. Joy — Industry Mentor

---

## Problem Statement

Job seekers in the IT domain face three key problems:

1. They do not know **which specific skills** they are missing for their target role
2. They do not know **which courses** to take to acquire those skills
3. They do not know **in what order** to take courses to build competency progressively

Existing platforms like LinkedIn Learning and Coursera provide generic recommendations without considering the user's existing skill profile or the real job market requirements of a specific role.

---

## Solution

RB-PLPE takes a learner's **current skills** and **target IT job role** as input, computes the exact **skill gap**, and generates a **personalised ordered learning pathway** of real online courses — covering **27 IT job roles** across the full IT spectrum.

```
User Input (Skills + Role)
        ↓
Stage 1: Skill Extraction (JobBERT)
        ↓
Stage 2: Knowledge Graph Lookup (Neo4j)
        ↓
Stage 3: Gap Analysis (NumPy + SciPy)
        ↓
Stage 4: Pathway Generation (PPO RL Agent)
        ↓
Personalised Learning Pathway
```

---

## System Architecture
<div align="center">
  <img src="data/raw/System_architecture_Diagram.jpg" alt="System Architecture" width="600" height = "600" >
</div>


```
┌─────────────────────────────────────────────────────────────┐
│                     USER LAYER                              │
│         Streamlit UI  ·  Registration + Form                │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP POST (JSON)
┌───────────────────────▼─────────────────────────────────────┐
│                   BACKEND LAYER                             │
│      FastAPI  ·  Pydantic Validation  ·  JWT Auth           │
│      PostgreSQL (users · skill_inputs · pathways)           │
└───────────────────────┬─────────────────────────────────────┘
                        │ Dispatches to ML Pipeline
┌───────────────────────▼─────────────────────────────────────┐
│               CORE ML PIPELINE (4 Stages)                   │
│                                                             │
│  [Stage 1]       [Stage 2]      [Stage 3]     [Stage 4]    │
│  BERT/JobBERT → Neo4j Graph → Gap Analysis →    PPO        │
│  Skill Extract   KG Lookup     Vector Math    RL Agent      │
└───────────────────────┬─────────────────────────────────────┘
                        │ Returns JSON
┌───────────────────────▼─────────────────────────────────────┐
│                   OUTPUT LAYER                              │
│   Gap Score · Missing Skills · Ordered Courses · Est. Weeks │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
Role_Based_Personalized_Learning_Pathway_Engine/
├── backend/                        # FastAPI Application Core
│   ├── database.py                 # PostgreSQL & Neo4j connection setup
│   ├── main.py                     # API entry point & 6 REST endpoints
│   ├── models.py                   # SQLAlchemy ORM table definitions
│   └── schemas.py                  # Pydantic request/response validation
│
├── ml/                             # Machine Learning Pipeline
│   ├── skill_extractor.py          # Stage 1: JobBERT skill extraction
│   ├── knowledge_graph.py          # Stage 2: Neo4j Cypher query handler
│   ├── gap_analysis.py             # Stage 3: Weighted gap vector calculator
│   └── pathway_generator.py        # Stage 4: PPO RL agent + Gymnasium env
│
├── frontend/                       # User Interface
│   └── app.py                      # Streamlit web application
│
├── data/                           # Dataset Management
│   ├── raw/
│   │   ├── naukri.csv              # 30,000 raw IT job postings (Naukri.com)
│   │   └── Online_Courses.csv      # 8,092 raw online courses
│   └── cleaned/
│       ├── courses_cleaned.csv     # 766 cleaned IT courses for PPO training
│       └── role_skill_mapping.csv  # 1,108 role-skill pairs for Neo4j
│
├── notebooks/                      # Data Engineering & Model Training
│   ├── 01_naukri_to_role_skill_mapping.ipynb   # Naukri data processing
│   ├── 02_online_courses_cleaning.ipynb         # Course data cleaning
│   └── 04_ppo_training.ipynb                   # PPO RL agent training
│
├── models/                         # Saved ML Artifacts
│   └── ppo_agent.zip               # Trained PPO model weights
│
├── tests/                          # Automated Testing Suite
│   ├── test_skill_extractor.py     # Precision, Recall, F1 tests
│   ├── test_gap_analysis.py        # Gap score accuracy tests
│   ├── test_knowledge_graph.py     # Neo4j connection & query tests
│   └── test_pathway_generator.py   # PPO environment & coverage tests
│
├── .env                            # Environment variables (not committed)
├── .python-version                 # Python version pin: 3.10.11
├── pyproject.toml                  # Project metadata & dependencies (uv)
├── uv.lock                         # Pinned lockfile for reproducibility
└── README.md                       # This file
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Python-native web UI |
| Backend | FastAPI + Uvicorn | REST API server |
| Validation | Pydantic v2 | Request/response schema validation |
| Auth | python-jose (JWT) | User session management |
| Relational DB | PostgreSQL 15 | Users, inputs, pathways storage |
| ORM | SQLAlchemy + Alembic | Database abstraction |
| Graph DB | Neo4j | Role-skill knowledge graph |
| Graph Query | Cypher | Graph traversal language |
| Stage 1 | JobBERT (HuggingFace) | Skill extraction via NER |
| Stage 2 | Neo4j Cypher | Role requirement lookup |
| Stage 3 | NumPy + SciPy | Gap vector computation |
| Stage 4 | PPO (Stable-Baselines3) | RL pathway generation |
| RL Env | Gymnasium | Custom learning environment |
| Data | Pandas + spaCy | Dataset cleaning |
| Dep. Manager | uv | Fast package management |

---

## Getting Started

### Prerequisites

- Python 3.10.11
- PostgreSQL 15
- Neo4j Desktop 5.x
- uv package manager

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/RB-PLPE.git
cd RB-PLPE
```

### 2. Create and activate virtual environment

```bash
uv venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv pip install fastapi uvicorn sqlalchemy psycopg2-binary "pydantic[email]" \
    python-dotenv python-jose streamlit plotly requests \
    transformers torch stable-baselines3 gymnasium \
    pandas numpy scipy neo4j
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/rbplpe_db
NEO4J_URI=bolt://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=yourpassword
```

### 5. Set up PostgreSQL

```bash
psql -U postgres
CREATE DATABASE rbplpe_db;
\q
```

### 6. Set up Neo4j

1. Open Neo4j Desktop
2. Create a new database named `rbplpe_db`
3. Start the database — must show **Running** (green) status

### 7. Prepare datasets

Place raw datasets in `data/raw/`:
- `naukri.csv`
- `Online_Courses.csv`

Run cleaning notebooks in order from VS Code:

```
notebooks/01_naukri_to_role_skill_mapping.ipynb
notebooks/02_online_courses_cleaning.ipynb
```

### 8. Load Knowledge Graph into Neo4j

```bash
cd ml
uv run python knowledge_graph.py
```

This runs `load_graph()` once to populate Neo4j with all role-skill relationships.

### 9. Train PPO Agent (optional)

```bash
# Run from VS Code:
notebooks/04_ppo_training.ipynb
# Output saved to: models/ppo_agent.zip
```

If `ppo_agent.zip` is not present, the system automatically falls back to rule-based pathway generation.

---

## Running the Application

Open **two terminals** and run simultaneously:

**Terminal 1 — FastAPI Backend:**
```bash
cd backend
uv run uvicorn main:app --reload
```
- Backend: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

**Terminal 2 — Streamlit Frontend:**
```bash
cd frontend
uv run streamlit run app.py
```
- Frontend: `http://localhost:8501`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| GET | `/` | Health check |
| POST | `/api/v1/register` | Register a new user |
| GET | `/api/v1/login` | Login with email |
| POST | `/api/v1/generate-pathway` | **Main — triggers full 4-stage ML pipeline** |
| GET | `/api/v1/history/{user_id}` | Fetch past pathways |
| GET | `/api/v1/roles` | Get all 27 valid IT roles |

### Main Endpoint — Request

```json
POST /api/v1/generate-pathway
{
    "user_id"       : 1,
    "skills"        : ["python", "sql", "pandas"],
    "target_role"   : "Data Scientist",
    "experience"    : "Fresher (0-1 years)",
    "hours_per_week": 5
}
```

### Main Endpoint — Response

```json
{
    "user_id"        : 1,
    "target_role"    : "Data Scientist",
    "gap_score"      : 0.57,
    "missing_skills" : ["machine learning", "statistics", "deep learning"],
    "pathway"        : [
        {
            "rank"        : 1,
            "course_title": "Machine Learning Specialization",
            "skills"      : "machine learning, statistics",
            "difficulty"  : "Beginner",
            "rating"      : 4.9,
            "course_url"  : "https://coursera.org/...",
            "duration_hrs": 60.0,
            "covers_skill": "machine learning",
            "platform"    : "Coursera"
        }
    ],
    "estimated_weeks": 14
}
```

---

## ML Pipeline Details

### Stage 1 — Skill Extractor

- **Model:** JobBERT (`jjzha/jobbert-base-cased`) — Transfer Learning
- **Input:** `"Python, SQL, basic ML, Pandas"`
- **Output:** `["python", "sql", "machine learning", "pandas"]`
- **Normalization:** Synonym map (`"ML"` → `"machine learning"`)

### Stage 2 — Knowledge Graph

- **Database:** Neo4j with Cypher queries
- **Graph:** `(Role)–[REQUIRES {importance}]→(Skill)`
- **importance_score** = `skill_count / total_jobs_for_that_role`
- **Data source:** 30,000 Naukri job postings → 1,108 role-skill pairs

### Stage 3 — Gap Analysis

- **Method:** Importance-weighted binary vector comparison
- **Gap score:** `Σ(missing_importance) / Σ(all_importance)`
- **Example:** User has python + sql but missing ml, stats, dl → gap = 0.57

### Stage 4 — PPO Pathway Generator

| RL Component | Value |
|-------------|-------|
| Algorithm | PPO (Proximal Policy Optimization) |
| State | Binary vector size 30 (29 skills + progress) |
| Action | Course index from 766-course pool |
| Reward | +10×(rating/5) per skill covered, −2 redundant, −5 duplicate |
| Training | 50,000 timesteps |
| Fallback | Rule-based when ppo_agent.zip not found |

---

## Database Schema

### PostgreSQL — 3 Tables

```
users          → id, name, email, created_at
skill_inputs   → user_id, raw_skills, parsed_skills, target_role,
                 experience, hours_per_week, gap_score, submitted_at
pathways       → user_id, skill_input_id, missing_skills,
                 courses_json, estimated_weeks, created_at
```

### Neo4j — Knowledge Graph

```cypher
(Role {name: "Data Scientist"})
    -[:REQUIRES {importance: 0.95}]→
(Skill {name: "python"})
```

---

## Supported IT Roles (27 Total)

```
Data & AI        : Data Scientist, ML Engineer, Data Analyst, Data Engineer,
                   AI Engineer, BI Analyst, NLP Engineer, Computer Vision Engineer
Web & Software   : Software Engineer, Frontend Developer, Backend Developer,
                   Full Stack Developer
Mobile           : Android Developer, iOS Developer, Mobile App Developer
DevOps & Cloud   : DevOps Engineer, Cloud Engineer
Security         : Cybersecurity Analyst
Database         : Database Administrator
QA               : QA Engineer
Network/Systems  : Network Engineer, System Administrator
Other IT         : UI/UX Designer, Business Analyst, Solutions Architect,
                   Tech Lead, Embedded Systems Engineer, Blockchain Developer
```

---

## Evaluation

| Stage | Metric | How to Measure |
|-------|--------|---------------|
| Skill Extractor | Precision, Recall, F1 | `tests/test_skill_extractor.py` |
| Knowledge Graph | Role Coverage Rate | `tests/test_knowledge_graph.py` |
| Gap Analysis | Gap Score Accuracy | `tests/test_gap_analysis.py` |
| PPO Agent | Avg Episode Reward (~190) | Training logs in notebook |
| PPO vs Rule-Based | Skill Coverage % | `tests/test_pathway_generator.py` |
| Full System | Response Time, Success Rate | End-to-end test via API |

---

## Running Tests

```bash
cd ml

uv run python ../tests/test_skill_extractor.py
uv run python ../tests/test_gap_analysis.py
uv run python ../tests/test_knowledge_graph.py
uv run python ../tests/test_pathway_generator.py
```

---

## Datasets

| Dataset | Raw | Cleaned | Used For |
|---------|-----|---------|---------|
| `naukri.csv` | 30,000 jobs × 11 cols | 1,108 role-skill pairs | Neo4j Knowledge Graph |
| `Online_Courses.csv` | 8,092 courses × 45 cols | 766 IT courses × 8 cols | PPO Course Pool |

---

## Known Limitations

- Dataset recency: Naukri (2019), Courses (2023) — emerging skills may be missing
- PPO trained on 50K timesteps — production benefits from 500K+
- Skill matching uses string containment — no semantic similarity
- Roles with few postings have less reliable importance scores
- No real-time dataset updates
- Currently local only — cloud deployment pending

---

## Cloud Deployment

| Component | Platform | Notes |
|-----------|---------|-------|
| Frontend | Streamlit Community Cloud | Free forever |
| Backend | Render Web Service | Free tier (sleeps after 15 min) |
| PostgreSQL | Render PostgreSQL | Free 90 days |
| Neo4j | Neo4j Aura Free | Free forever, 200MB limit |

---

## License

Academic project — UPES MCA Data Science 2024–2026. All rights reserved.

---

## Acknowledgements

- **JobBERT** by jjzha — HuggingFace pretrained NER model
- **Stable-Baselines3** — PPO reinforcement learning implementation
- **Neo4j** — Graph database platform
- **Naukri.com** — Job postings dataset source
- **Coursera, Udacity, Simplilearn, FutureLearn** — Course data sources

---

<div align="center">

**Built with ❤️ by Team DS7 | UPES MCA Data Science 2024–2026**

*Hamant Jagwan · Tanuj Sanwal · Pawan Singh Rajwar*

</div>