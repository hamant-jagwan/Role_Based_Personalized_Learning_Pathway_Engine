from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import sys
import os

# ── Add ml/ folder to path so imports work ──
sys.path.append(os.path.join(os.path.dirname(__file__), "../ml"))

from database import engine, get_db, Base
from models   import User, SkillInput, Pathway
from schemas  import (
    UserCreate, UserResponse,
    PathwayRequest, PathwayResponse,
    HistoryItem
)
# ── Import ML pipeline stages ─────────────────
from skill_extractor   import extract_skills
from knowledge_graph   import get_role_requirements, get_role_requirements_with_importance
from gap_analysis      import compute_gap, estimate_weeks
from pathway_generator import generate_pathway


# ── Create all tables on startup ──────────────
Base.metadata.create_all(bind=engine)

# ── FastAPI app instance ──────────────────────
app = FastAPI(
    title       = "RB-PLPE API",
    description = "Role-Based Personalised Learning Pathway Engine",
    version     = "1.0.0"
)



# ROUTE 1 — Health check

@app.get("/")
def root():
    return {"status": "RB-PLPE API is running"}



# ROUTE 2 — Register a new user
# POST /api/v1/register

@app.post("/api/v1/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):

    # Check if email already exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user row
    new_user = User(
        name  = user_data.name,
        email = user_data.email
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user



# ROUTE 3 — Generate learning pathway  ← MAIN ROUTE
# POST /api/v1/generate-pathway

@app.post("/api/v1/generate-pathway", response_model=PathwayResponse)
def generate_pathway_route(request: PathwayRequest, db: Session = Depends(get_db)):

    # ── Step 1: Check user exists ──────────────
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ── Step 2: Save user input to DB ──────────
    skill_input = SkillInput(
        user_id        = request.user_id,
        raw_skills     = ", ".join(request.skills),
        parsed_skills  = ",".join(request.skills),
        target_role    = request.target_role,
        experience     = request.experience,
        hours_per_week = request.hours_per_week,
        gap_score      = None
    )
    db.add(skill_input)
    db.commit()
    db.refresh(skill_input)

    # ── Step 3: ML Pipeline ────────────────────
# ── Step 3: ML Pipeline ────────────────────
    try:
        # Stage 1
        print("Stage 1 starting...")
        normalized_skills = extract_skills(", ".join(request.skills))
        print(f"Stage 1 done: {normalized_skills}")

        # Stage 2
        print("Stage 2 starting...")
        required_skills   = get_role_requirements(request.target_role)
        importance_scores = get_role_requirements_with_importance(request.target_role)
        print(f"Stage 2 done: {required_skills[:5]}")

        # Stage 3
        print("Stage 3 starting...")
        gap_result      = compute_gap(normalized_skills, required_skills, importance_scores)
        gap_score       = gap_result["gap_score"]
        missing_skills  = gap_result["missing_skills"]
        print(f"Stage 3 done: gap={gap_score}, missing={missing_skills[:3]}")

        # Stage 4
        print("Stage 4 starting...")
        pathway_courses = generate_pathway(
            missing_skills = missing_skills,
            hours_per_week = request.hours_per_week,
            experience     = request.experience
        )
        print(f"Stage 4 done: {len(pathway_courses)} courses")

        estimated_weeks = estimate_weeks(missing_skills, request.hours_per_week)

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"ML pipeline error: {str(e)}")
    
    # ── Step 4: Update gap score in DB ─────────
    skill_input.gap_score = gap_score
    db.commit()

    # ── Step 5: Save pathway to DB ─────────────
    pathway_record = Pathway(
        user_id         = request.user_id,
        skill_input_id  = skill_input.id,
        missing_skills  = ",".join(missing_skills),
        courses_json    = json.dumps(pathway_courses),
        estimated_weeks = estimated_weeks
    )
    db.add(pathway_record)
    db.commit()

    # ── Step 6: Return response ─────────────────
    return PathwayResponse(
        user_id         = request.user_id,
        target_role     = request.target_role,
        gap_score       = gap_score,
        missing_skills  = missing_skills,
        pathway         = pathway_courses,
        estimated_weeks = estimated_weeks
    )



# ROUTE 4 — Get past pathways for a user
# GET /api/v1/history/{user_id}

@app.get("/api/v1/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    pathways = (
        db.query(Pathway)
        .filter(Pathway.user_id == user_id)
        .order_by(Pathway.created_at.desc())
        .all()
    )

    result = []
    for p in pathways:
        result.append({
            "pathway_id"     : p.id,
            "target_role"    : p.skill_input.target_role,
            "gap_score"      : p.skill_input.gap_score,
            "estimated_weeks": p.estimated_weeks,
            "created_at"     : p.created_at
        })

    return {"user_id": user_id, "history": result}



# ROUTE 5 — Get all valid job roles
# GET /api/v1/roles

@app.get("/api/v1/roles")
def get_roles():
    return {
        "roles": [
            "Data Scientist",
            "Machine Learning Engineer",
            "Data Analyst",
            "Data Engineer",
            "AI Engineer",
            "Business Intelligence Analyst",
            "NLP Engineer",
            "Computer Vision Engineer",
            "Software Engineer",
            "Frontend Developer",
            "Backend Developer",
            "Full Stack Developer",
            "DevOps Engineer",
            "Cloud Engineer",
            "Cybersecurity Analyst",
            "Database Administrator",
            "Android Developer",
            "iOS Developer",
            "Mobile App Developer",
            "QA Engineer",
            "Network Engineer",
            "System Administrator",
            "UI/UX Designer",
            "Business Analyst",
            "Solutions Architect",
            "Tech Lead",
            "Embedded Systems Engineer",
            "Blockchain Developer",
        ]
    }


# ROUTE 6 — Login existing user by email
# GET /api/v1/login?email=hamant@gmail.com

@app.get("/api/v1/login")
def login_user(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    return {
        "id"        : user.id,
        "name"      : user.name,
        "email"     : user.email,
        "created_at": user.created_at
    }