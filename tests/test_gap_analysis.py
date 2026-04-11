import sys
import os

# ── Add ml/ folder to path (same as backend) ──
sys.path.append(os.path.join(os.path.dirname(__file__), "../ml"))
from gap_analysis import compute_gap

# Test cases with known expected gap
test_cases = [
    {
        "label"    : "No gap — user has all skills",
        "user"     : ["python", "sql", "machine learning", "statistics", "deep learning"],
        "required" : ["python", "sql", "machine learning", "statistics", "deep learning"],
        "expected_gap" : 0.0,
    },
    {
        "label"    : "Full gap — user has no skills",
        "user"     : [],
        "required" : ["python", "sql", "machine learning", "statistics", "deep learning"],
        "expected_gap" : 1.0,
    },
    {
        "label"    : "Partial gap — user has 2 of 5 skills",
        "user"     : ["python", "sql"],
        "required" : ["python", "sql", "machine learning", "statistics", "deep learning"],
        "expected_gap" : 0.6,   # roughly
    },
]

print("GAP ANALYSIS EVALUATION")
print("=" * 55)

for tc in test_cases:
    result = compute_gap(tc["user"], tc["required"])
    error  = abs(result["gap_score"] - tc["expected_gap"])

    print(f"\nTest     : {tc['label']}")
    print(f"Expected gap : {tc['expected_gap']:.2f}")
    print(f"Got gap      : {result['gap_score']:.2f}")
    print(f"Error        : {error:.2f}")
    print(f"Coverage     : {result['coverage_pct']}%")
    print(f"Missing      : {result['missing_skills']}")