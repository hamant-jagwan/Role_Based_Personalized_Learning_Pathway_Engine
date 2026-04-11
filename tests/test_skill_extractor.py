import sys
import os

# ── Add ml/ folder to path (same as backend) ──
sys.path.append(os.path.join(os.path.dirname(__file__), "../ml"))

# Now this will work
from skill_extractor import extract_skills

# Ground truth test cases
test_cases = [
    {
        "input"   : "Python, SQL, Pandas, basic Machine Learning",
        "expected": ["python", "sql", "pandas", "machine learning"]
    },
    {
        "input"   : "I know JavaScript, React and Node.js",
        "expected": ["javascript", "react", "node"]
    },
    {
        "input"   : "Java, Spring Boot, Docker, Kubernetes, AWS",
        "expected": ["java", "spring boot", "docker", "kubernetes", "aws"]
    },
    {
        "input"   : "deep learning, tensorflow, computer vision, python",
        "expected": ["deep learning", "tensorflow", "computer vision", "python"]
    },
    {
        "input"   : "SQL, data visualization, statistics, Excel",
        "expected": ["sql", "data visualization", "statistics", "excel"]
    },
]

total_precision = []
total_recall    = []
total_f1        = []

for tc in test_cases:
    actual   = set(extract_skills(tc["input"]))
    expected = set(tc["expected"])

    tp = len(actual & expected)          # correctly extracted
    fp = len(actual - expected)          # extracted but wrong
    fn = len(expected - actual)          # missed

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    total_precision.append(precision)
    total_recall.append(recall)
    total_f1.append(f1)

    print(f"Input    : {tc['input']}")
    print(f"Expected : {sorted(expected)}")
    print(f"Got      : {sorted(actual)}")
    print(f"P={precision:.2f}  R={recall:.2f}  F1={f1:.2f}")
    print()

print("=" * 40)
print(f"Avg Precision : {sum(total_precision)/len(total_precision):.2f}")
print(f"Avg Recall    : {sum(total_recall)/len(total_recall):.2f}")
print(f"Avg F1 Score  : {sum(total_f1)/len(total_f1):.2f}")