# Defines what your PostgreSQL tables look like
# Each class = one table in the database
# Each variable inside = one column

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# TABLE 1: users
# Stores every person who uses the app

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)   # auto increment ID
    name       = Column(String(100), nullable=False)             # full name
    email      = Column(String(150), unique=True, nullable=False) # must be unique
    created_at = Column(DateTime, server_default=func.now())     # auto timestamp

    # Relationship: one user can have many skill inputs
    skill_inputs = relationship("SkillInput", back_populates="user")
    pathways     = relationship("Pathway",    back_populates="user")


# ── TABLE 2: skill_inputs ─────────────────────
# Stores every form submission (what user typed)
class SkillInput(Base):
    __tablename__ = "skill_inputs"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"), nullable=False)  # links to users table
    raw_skills     = Column(Text,    nullable=False)   # original text: "Python, SQL, Pandas"
    parsed_skills  = Column(Text,    nullable=False)   # cleaned list stored as string: "python,sql,pandas"
    target_role    = Column(String(100), nullable=False)  # "Data Scientist"
    experience     = Column(String(50),  nullable=False)  # "Fresher"
    hours_per_week = Column(Integer,     nullable=False)  # 5
    gap_score      = Column(Float,       nullable=True)   # filled after ML pipeline runs: 0.57
    submitted_at   = Column(DateTime,    server_default=func.now())
        # Relationship back to user
    user    = relationship("User",    back_populates="skill_inputs")
    pathway = relationship("Pathway", back_populates="skill_input", uselist=False)

# ── TABLE 3: pathways ─────────────────────────
# Stores the generated learning pathway for each input
class Pathway(Base):
    __tablename__ = "pathways"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"),        nullable=False)
    skill_input_id  = Column(Integer, ForeignKey("skill_inputs.id"), nullable=False)
    missing_skills  = Column(Text,  nullable=False)  # comma-separated: "deep_learning,statistics"
    courses_json    = Column(Text,  nullable=False)  # full pathway stored as JSON string
    estimated_weeks = Column(Integer, nullable=False) # 14
    created_at      = Column(DateTime, server_default=func.now())

    # Relationships
    user        = relationship("User",       back_populates="pathways")
    skill_input = relationship("SkillInput", back_populates="pathway")


