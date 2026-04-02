# ml/pathway_generator.py

# Stage 4 of ML Pipeline — Pathway Generator
# Uses PPO Reinforcement Learning agent to
# generate optimal ordered course sequence


import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from typing import List, Dict
import os

# Paths 
COURSES_PATH = "../data/cleaned/courses_cleaned.csv"
MODEL_PATH   = "../models/ppo_agent"

# Training skills — must match what model was trained on 
# These are the 29 skills used during PPO training
# Observation size = len(TRAINING_SKILLS) + 1 = 30

TRAINING_SKILLS = [
    # Data & ML
    "machine learning", "deep learning", "python", "sql",
    "data visualization", "statistics", "data analysis",
    "pandas", "numpy", "tensorflow",
    # Web & Software
    "javascript", "react", "node", "html", "css",
    "java", "python programming", "rest api",
    # DevOps & Cloud
    "docker", "kubernetes", "aws", "devops", "linux",
    # Security & DB
    "cybersecurity", "database management", "mysql",
    # Other IT
    "project management", "agile", "git"
]



# CUSTOM GYM ENVIRONMENT

class LearningPathEnv(gym.Env):
    """
    Custom Gymnasium environment for pathway generation

    State  → Binary vector of size len(skill_list) + 1
             1 = skill still missing, 0 = covered
             Last element = normalized step progress
    Action → Course index from course pool
    Reward → Positive for covering skills, negative for redundancy
    """

    metadata = {"render_modes": []}

    def __init__(self, courses_df: pd.DataFrame, skill_list: List[str], max_steps: int = None):
        super().__init__()

        self.courses_df  = courses_df.reset_index(drop=True)
        self.skill_list  = [s.strip().lower() for s in skill_list]
        self.n_courses   = len(self.courses_df)
        self.n_skills    = len(self.skill_list)
        self.max_steps   = max_steps or min(15, self.n_skills * 3)

        # Action space: pick any course
        self.action_space = spaces.Discrete(self.n_courses)

        # Observation: skill coverage vector + progress
        self.observation_space = spaces.Box(
            low   = 0.0,
            high  = 1.0,
            shape = (self.n_skills + 1,),
            dtype = np.float32
        )

        self.reset()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.skill_coverage   = np.ones(self.n_skills, dtype=np.float32)
        self.selected_courses = set()
        self.current_step     = 0
        return self._get_obs(), {}

    def _get_obs(self):
        progress = np.array([self.current_step / self.max_steps], dtype=np.float32)
        return np.concatenate([self.skill_coverage, progress])

    def step(self, action):
        self.current_step += 1
        reward = 0.0

        course        = self.courses_df.iloc[int(action)]
        course_skills = str(course["skills"]).lower()
        course_rating = float(course["rating"])
        course_diff   = str(course["difficulty"])

        # Reward: cover missing skills
        skills_covered = []
        for i, skill in enumerate(self.skill_list):
            if skill in course_skills and self.skill_coverage[i] == 1.0:
                self.skill_coverage[i] = 0.0
                reward += 10.0 * (course_rating / 5.0)
                skills_covered.append(skill)

        # Penalty: redundant course
        if len(skills_covered) == 0:
            reward -= 2.0

        # Penalty: duplicate course
        if action in self.selected_courses:
            reward -= 5.0
        else:
            self.selected_courses.add(action)

        # Bonus: correct difficulty ordering
        if course_diff == "Beginner"     and self.current_step <= 3:  reward += 1.5
        elif course_diff == "Intermediate" and 3 < self.current_step <= 7: reward += 1.0
        elif course_diff == "Advanced"   and self.current_step > 7:   reward += 2.0

        terminated = bool(np.sum(self.skill_coverage) == 0)
        truncated  = bool(self.current_step >= self.max_steps and not terminated)

        return self._get_obs(), reward, terminated, truncated, {
            "skills_covered": skills_covered,
            "total_covered" : int(self.n_skills - np.sum(self.skill_coverage))
        }

    def render(self):
        pass



# FUNCTION 1 — Generate Pathway
# Called by FastAPI during ML pipeline

def generate_pathway(
    missing_skills : List[str],
    hours_per_week : int,
    experience     : str = "Fresher (0-1 years)"
) -> List[Dict]:
    """
    Input:
        missing_skills → ["machine learning", "deep learning", "statistics"]
        hours_per_week → 5
        experience     → "Fresher (0-1 years)"

    Output:
        List of course dicts in optimal order
    """

    # Load courses
    courses_df = pd.read_csv(COURSES_PATH)
    courses_df = courses_df.dropna(subset=["skills"]).reset_index(drop=True)

    # Filter by experience level
    courses_df = _filter_by_experience(courses_df, experience)

    # Try PPO model first
    ppo_model_file = MODEL_PATH + ".zip"
    if os.path.exists(ppo_model_file):
        print("Using trained PPO agent")
        pathway = _generate_with_ppo(courses_df, missing_skills)
    else:
        print("PPO model not found — using rule-based fallback")
        pathway = _generate_rule_based(courses_df, missing_skills)

    # Add rank numbers
    for i, course in enumerate(pathway):
        course["rank"] = i + 1

    return pathway



# Generate with PPO (fixed obs size)

def _generate_with_ppo(courses_df: pd.DataFrame, missing_skills: List[str]) -> List[Dict]:
    """
    KEY FIX: The PPO model was trained with TRAINING_SKILLS (29 skills).
    Observation size is always 30 (29 + 1 progress).

    We always use TRAINING_SKILLS as the environment skill list.
    But we only add courses to the pathway if they cover one of
    the user's actual missing_skills.
    """
    model = PPO.load(MODEL_PATH)

    # ── IMPORTANT: use TRAINING_SKILLS not missing_skills ──
    # This keeps observation size = 30 matching what model expects
    env = LearningPathEnv(courses_df, TRAINING_SKILLS)

    # Mark which training skills are actually missing for this user
    user_missing = set(s.strip().lower() for s in missing_skills)

    obs, _  = env.reset()
    pathway = []
    done    = False
    seen    = set()

    while not done and len(pathway) < len(missing_skills) + 3:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, terminated, truncated, info = env.step(int(action))
        done = terminated or truncated

        course = courses_df.iloc[int(action)]

        # Only include course if it covers one of user's actual missing skills
        covers = _find_covered_skill(str(course["skills"]), list(user_missing))
        title  = course["course_title"]

        if covers and title not in seen:
            seen.add(title)
            pathway.append({
                "course_title": title,
                "skills"      : course["skills"],
                "difficulty"  : course["difficulty"],
                "rating"      : float(course["rating"]),
                "course_url"  : course["course_url"],
                "duration_hrs": float(course["duration_hrs"]),
                "covers_skill": covers,
                "platform"    : course.get("platform", "Online"),
            })
            user_missing.discard(covers)

        # Stop when all user missing skills are covered
        if len(user_missing) == 0:
            break

    # If PPO missed some skills, fill gaps with rule-based
    if user_missing:
        remaining = _generate_rule_based(courses_df, list(user_missing))
        pathway.extend(remaining)

    return pathway



# Rule-based fallback

def _generate_rule_based(courses_df: pd.DataFrame, missing_skills: List[str]) -> List[Dict]:
    """
    For each missing skill → find best rated matching course
    Order: Beginner → Intermediate → Advanced
    """
    pathway      = []
    used_courses = set()

    for skill in missing_skills:
        for difficulty in ["Beginner", "Intermediate", "Advanced"]:
            mask = (
                courses_df["skills"].str.lower().str.contains(skill, na=False, regex=False) &
                (courses_df["difficulty"] == difficulty)
            )
            matched = courses_df[mask]
            matched = matched[~matched.index.isin(used_courses)]

            if len(matched) > 0:
                best = matched.sort_values("rating", ascending=False).iloc[0]
                used_courses.add(best.name)
                pathway.append({
                    "course_title": best["course_title"],
                    "skills"      : best["skills"],
                    "difficulty"  : best["difficulty"],
                    "rating"      : float(best["rating"]),
                    "course_url"  : best["course_url"],
                    "duration_hrs": float(best["duration_hrs"]),
                    "covers_skill": skill,
                    "platform"    : best.get("platform", "Online"),
                })
                break

    return pathway


# HELPER — Filter by experience level

def _filter_by_experience(courses_df: pd.DataFrame, experience: str) -> pd.DataFrame:
    if "Fresher" in experience:
        return courses_df[courses_df["difficulty"].isin(["Beginner", "Intermediate"])]
    elif "Mid" in experience:
        return courses_df[courses_df["difficulty"].isin(["Intermediate", "Advanced"])]
    return courses_df



# HELPER — Find which missing skill a course covers

def _find_covered_skill(course_skills: str, missing_skills: List[str]) -> str:
    course_skills_lower = course_skills.lower()
    for skill in missing_skills:
        if skill.lower() in course_skills_lower:
            return skill
    return ""



# TEST — Run directly
# uv run python pathway_generator.py

if __name__ == "__main__":

    print("=" * 55)
    print("PATHWAY GENERATOR TEST")
    print("=" * 55)

    missing_skills = ["machine learning", "deep learning", "statistics", "data visualization"]

    print(f"\nMissing skills : {missing_skills}")
    print(f"Hours/week     : 5")
    print(f"Experience     : Fresher")

    pathway = generate_pathway(
        missing_skills = missing_skills,
        hours_per_week = 5,
        experience     = "Fresher (0-1 years)"
    )

    print(f"\nPathway ({len(pathway)} courses):")
    for course in pathway:
        print(f"\n  Rank     : {course['rank']}")
        print(f"  Title    : {course['course_title']}")
        print(f"  Covers   : {course['covers_skill']}")
        print(f"  Level    : {course['difficulty']}")
        print(f"  Rating   : {course['rating']}")
        print(f"  Duration : {course['duration_hrs']} hrs")
        print(f"  Platform : {course['platform']}")

    print("\nDone!")