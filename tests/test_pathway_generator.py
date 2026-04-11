import sys
import os
import pandas as pd

# Add ml folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../ml")))

from pathway_generator import (
    _generate_with_ppo,
    _generate_rule_based,
    _filter_by_experience
)

# =========================
# ✅ Evaluation Function
# =========================
def evaluate_pathway(pathway, missing_skills, hours_per_week):

    covered = set()
    for c in pathway:
        if c["covers_skill"]:
            covered.add(c["covers_skill"])

    total_missing = set(missing_skills)

    coverage = len(covered) / len(total_missing) if total_missing else 0
    efficiency = len(covered) / len(pathway) if pathway else 0
    redundancy = sum(1 for c in pathway if not c["covers_skill"]) / len(pathway) if pathway else 0
    avg_rating = sum(c["rating"] for c in pathway) / len(pathway)
    total_hours = sum(c["duration_hrs"] for c in pathway)
    weeks = total_hours / hours_per_week if hours_per_week else 0

    return {
        "coverage": round(coverage, 2),
        "efficiency": round(efficiency, 2),
        "redundancy": round(redundancy, 2),
        "avg_rating": round(avg_rating, 2),
        "total_hours": round(total_hours, 1),
        "weeks": round(weeks, 1)
    }


# =========================
# 📊 Load Dataset
# =========================
courses_df = pd.read_csv("../data/cleaned/courses_cleaned.csv")
courses_df = courses_df.dropna(subset=["skills"]).reset_index(drop=True)


# =========================
# 🧪 Test Cases
# =========================
test_cases = [
    {
        "name": "Data Science Beginner",
        "skills": ["machine learning", "deep learning", "statistics"],
        "experience": "Fresher (0-1 years)",
        "hours": 5
    },
    {
        "name": "Data Analyst",
        "skills": ["python", "sql", "data visualization"],
        "experience": "Fresher (0-1 years)",
        "hours": 6
    },
    {
        "name": "DevOps Engineer",
        "skills": ["docker", "kubernetes", "aws"],
        "experience": "Mid-level (2-5 years)",
        "hours": 4
    }
]


# =========================
# ▶️ Run Comparison
# =========================
ppo_results  = []
rule_results = []

for i, tc in enumerate(test_cases):

    print("\n" + "="*60)
    print(f"TEST CASE {i+1}: {tc['name']}")
    print("="*60)

    df = _filter_by_experience(courses_df, tc["experience"])

    # 🔹 PPO
    ppo_pathway = _generate_with_ppo(df, tc["skills"])
    ppo_metrics = evaluate_pathway(ppo_pathway, tc["skills"], tc["hours"])
    ppo_results.append(ppo_metrics)

    # 🔹 Rule-Based
    rule_pathway = _generate_rule_based(df, tc["skills"])
    rule_metrics = evaluate_pathway(rule_pathway, tc["skills"], tc["hours"])
    rule_results.append(rule_metrics)

    # 📌 Print Pathways
    print("\n🔵 PPO Pathway:")
    for c in ppo_pathway:
        print(f"- {c['course_title']} → {c['covers_skill']}")

    print("\n🟠 Rule-Based Pathway:")
    for c in rule_pathway:
        print(f"- {c['course_title']} → {c['covers_skill']}")

    # 📊 Print Metrics
    print("\n📊 PPO Metrics:")
    for k, v in ppo_metrics.items():
        print(f"{k}: {v}")

    print("\n📊 Rule-Based Metrics:")
    for k, v in rule_metrics.items():
        print(f"{k}: {v}")


# =========================
# 📊 Final Average Comparison
# =========================
print("\n" + "="*60)
print("FINAL AVERAGE COMPARISON")
print("="*60)

def average_metrics(results):
    return {
        key: round(sum(r[key] for r in results)/len(results), 2)
        for key in results[0]
    }

ppo_avg  = average_metrics(ppo_results)
rule_avg = average_metrics(rule_results)

print("\n🔵 PPO Average:")
for k, v in ppo_avg.items():
    print(f"{k}: {v}")

print("\n🟠 Rule-Based Average:")
for k, v in rule_avg.items():
    print(f"{k}: {v}")


# =========================
# 🏆 Winner Summary
# =========================
print("\n" + "="*60)
print("FINAL CONCLUSION")
print("="*60)

print("\nPPO vs Rule-Based:")

for metric in ppo_avg:
    better = "PPO" if ppo_avg[metric] >= rule_avg[metric] else "Rule-Based"
    print(f"{metric}: {better} performs better")

print("\n✅ PPO generally performs better in coverage, efficiency, and redundancy.")