#ML Pipeline — Skill Gap Analysis
# Takes user skills + role requirements
# Returns gap score + missing skills

import numpy as np
from typing import List, Dict, Tuple



# FUNCTION 1 — Main Gap Analysis
# Called by FastAPI during ML pipeline Stage 3

def compute_gap(
    user_skills     : List[str],
    required_skills : List[str],
    importance_scores: Dict[str, float] = None
) -> Dict:
    """
    Input:
        user_skills      → ["python", "sql", "pandas"]
        required_skills  → ["python", "sql", "machine learning", "deep learning", "statistics"]
        importance_scores→ {"python": 0.95, "machine learning": 0.80, ...}  (optional)

    Output:
        {
            "gap_score"      : 0.57,
            "missing_skills" : ["machine learning", "deep learning", "statistics"],
            "matched_skills" : ["python", "sql"],
            "coverage_pct"   : 43.0,
            "user_vector"    : [1, 1, 0, 0, 0],
            "role_vector"    : [1, 1, 1, 1, 1]
        }
    """

    # ── Step 1: Normalize both lists to lowercase ──
    user_skills_clean     = [s.strip().lower() for s in user_skills]
    required_skills_clean = [s.strip().lower() for s in required_skills]

    # ── Step 2: Build binary vectors ──────────────
    # user_vector  → 1 if user has the skill, 0 if not
    # role_vector  → all 1s (role requires all skills)
    user_vector = []
    role_vector = []

    for skill in required_skills_clean:
        role_vector.append(1)
        # Check if user has this skill (partial match allowed)
        has_skill = any(
            skill in u_skill or u_skill in skill
            for u_skill in user_skills_clean
        )
        user_vector.append(1 if has_skill else 0)

    user_vec = np.array(user_vector, dtype=float)
    role_vec = np.array(role_vector, dtype=float)

    # ── Step 3: Find missing and matched skills ───
    missing_skills = []
    matched_skills = []

    for i, skill in enumerate(required_skills_clean):
        if user_vector[i] == 0:
            missing_skills.append(skill)
        else:
            matched_skills.append(skill)

    # ── Step 4: Calculate gap score ───────────────
    # If importance scores provided → weighted gap
    # Otherwise → simple ratio
    if importance_scores and len(importance_scores) > 0:
        gap_score = _weighted_gap_score(
            required_skills_clean,
            user_vector,
            importance_scores
        )
    else:
        # Simple gap score = missing / total
        gap_score = len(missing_skills) / len(required_skills_clean) if required_skills_clean else 0.0

    gap_score    = round(gap_score, 2)
    coverage_pct = round((1 - gap_score) * 100, 1)

    # ── Step 5: Sort missing skills by importance ─
    if importance_scores:
        missing_skills = sorted(
            missing_skills,
            key=lambda s: importance_scores.get(s, 0),
            reverse=True
        )

    return {
        "gap_score"      : gap_score,
        "missing_skills" : missing_skills,
        "matched_skills" : matched_skills,
        "coverage_pct"   : coverage_pct,
        "user_vector"    : user_vector,
        "role_vector"    : role_vector,
        "total_required" : len(required_skills_clean),
        "total_matched"  : len(matched_skills),
        "total_missing"  : len(missing_skills),
    }



# Weighted Gap Score
# Skills with higher importance count more

def _weighted_gap_score(
    required_skills  : List[str],
    user_vector      : List[int],
    importance_scores: Dict[str, float]
) -> float:
    """
    Weighted gap score using importance scores from Neo4j
    High importance missing skills → higher gap score
    """
    total_weight   = 0.0
    missing_weight = 0.0

    for i, skill in enumerate(required_skills):
        weight = importance_scores.get(skill, 0.1)  # default 0.1 if not found
        total_weight += weight
        if user_vector[i] == 0:
            missing_weight += weight

    if total_weight == 0:
        return 0.0

    return missing_weight / total_weight



# FUNCTION 2 — Estimate completion weeks

def estimate_weeks(
    missing_skills   : List[str],
    hours_per_week   : int,
    courses_df       = None
) -> int:
    """
    Estimates how many weeks to complete the pathway

    Input:
        missing_skills → ["machine learning", "deep learning"]
        hours_per_week → 5
        courses_df     → cleaned courses dataframe (optional)

    Output:
        estimated_weeks → 14
    """
    if courses_df is not None and len(courses_df) > 0:
        # Match courses to missing skills and sum duration
        total_hours = 0.0
        for skill in missing_skills:
            # Find best matching course for this skill
            mask = courses_df["skills"].str.lower().str.contains(skill, na=False, regex=False)
            
            matched = courses_df[mask]
            if len(matched) > 0:
                # Pick highest rated course
                best = matched.sort_values("rating", ascending=False).iloc[0]
                total_hours += best["duration_hrs"]
            else:
                total_hours += 20   # default 20 hrs if no course found

        weeks = max(1, round(total_hours / hours_per_week))
    else:
        # Rough estimate: 20 hours per missing skill
        total_hours = len(missing_skills) * 20
        weeks = max(1, round(total_hours / hours_per_week))

    return weeks



# TEST — Run directly to test
# uv run python gap_analysis.py

if __name__ == "__main__":

    print("=" * 55)
    print("GAP ANALYSIS TEST")
    print("=" * 55)

    # Simulated Stage 1 output (BERT)
    user_skills = ["python", "sql", "pandas", "excel"]

    # Simulated Stage 2 output (Neo4j)
    required_skills = [
        "python", "sql", "machine learning",
        "deep learning", "statistics",
        "data visualization", "feature engineering"
    ]

    # Simulated importance scores from Neo4j
    importance_scores = {
        "python"              : 0.95,
        "sql"                 : 0.85,
        "machine learning"    : 0.80,
        "deep learning"       : 0.75,
        "statistics"          : 0.70,
        "data visualization"  : 0.60,
        "feature engineering" : 0.55,
    }

    # Run gap analysis
    result = compute_gap(user_skills, required_skills, importance_scores)

    print(f"\nUser Skills     : {user_skills}")
    print(f"Required Skills : {required_skills}")
    print(f"\nGap Score       : {result['gap_score']}  ({result['gap_score']*100:.0f}% missing)")
    print(f"Coverage        : {result['coverage_pct']}% skills matched")
    print(f"\nMatched Skills  : {result['matched_skills']}")
    print(f"Missing Skills  : {result['missing_skills']}")
    print(f"\nTotal Required  : {result['total_required']}")
    print(f"Total Matched   : {result['total_matched']}")
    print(f"Total Missing   : {result['total_missing']}")

    print(f"\nUser Vector     : {result['user_vector']}")
    print(f"Role Vector     : {result['role_vector']}")

    # Test estimate weeks
    weeks = estimate_weeks(result["missing_skills"], hours_per_week=5)
    print(f"\nEstimated Weeks : {weeks} weeks at 5 hrs/week")

    print("\nDone!")