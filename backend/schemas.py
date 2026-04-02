# Pydantic request/response models
# Validates all data coming in and going out

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime

# ALL VALID ROLES — must match app.py dropdown

VALID_ROLES = [
    # Data & AI
    "Data Scientist",
    "Machine Learning Engineer",
    "Data Analyst",
    "Data Engineer",
    "AI Engineer",
    "Business Intelligence Analyst",
    "NLP Engineer",
    "Computer Vision Engineer",
    # Web & Software
    "Software Engineer",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    # Mobile
    "Android Developer",
    "iOS Developer",
    "Mobile App Developer",
    # DevOps & Cloud
    "DevOps Engineer",
    "Cloud Engineer",
    # Security
    "Cybersecurity Analyst",
    # Database
    "Database Administrator",
    # QA
    "QA Engineer",
    # Network & Systems
    "Network Engineer",
    "System Administrator",
    # Design & Other IT
    "UI/UX Designer",
    "Business Analyst",
    "Solutions Architect",
    "Tech Lead",
    "Embedded Systems Engineer",
    "Blockchain Developer",
]

# REQUEST SCHEMAS — data coming IN

class UserCreate(BaseModel):
    name  : str
    email : EmailStr


class PathwayRequest(BaseModel):
    user_id        : int
    skills         : List[str]
    target_role    : str
    experience     : str
    hours_per_week : int

    @field_validator("skills")
    def skills_not_empty(cls, v):
        if not v:
            raise ValueError("Skills list cannot be empty")
        return v

    @field_validator("target_role")
    def role_must_be_valid(cls, v):
        if v not in VALID_ROLES:
            raise ValueError(f"Target role '{v}' is not a valid role")
        return v

    @field_validator("hours_per_week")
    def hours_must_be_positive(cls, v):
        if v < 1 or v > 40:
            raise ValueError("Hours per week must be between 1 and 40")
        return v

# RESPONSE SCHEMAS — data going OUT

class CourseItem(BaseModel):
    rank         : int
    course_title : str
    skills       : str
    difficulty   : str
    rating       : float
    course_url   : str
    duration_hrs : float
    covers_skill : str
    platform     : Optional[str] = "Online"


class PathwayResponse(BaseModel):
    user_id         : int
    target_role     : str
    gap_score       : float
    missing_skills  : List[str]
    pathway         : List[dict]
    estimated_weeks : int


from pydantic import ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id         : int
    name       : str
    email      : str
    created_at : datetime


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id              : int
    target_role     : str
    gap_score       : Optional[float]
    estimated_weeks : int
    created_at      : datetime
