# ML Pipeline — Skill Extractor
# Extracts and normalizes skills from raw user text

from typing import List

# Synonym map
SYNONYM_MAP = {
    "ml"                               : "machine learning",
    "ai"                               : "artificial intelligence",
    "dl"                               : "deep learning",
    "nlp"                              : "natural language processing",
    "cv"                               : "computer vision",
    "js"                               : "javascript",
    "ts"                               : "typescript",
    "k8s"                              : "kubernetes",
    "oop"                              : "object oriented programming",
    "oops"                             : "object oriented programming",
    "dsa"                              : "data structures and algorithms",
    "dbms"                             : "database management",
    "stats"                            : "statistics",
    "tf"                               : "tensorflow",
    "sklearn"                          : "scikit-learn",
    "scikit learn"                     : "scikit-learn",
    "reactjs"                          : "react",
    "react.js"                         : "react",
    "nodejs"                           : "node",
    "node.js"                          : "node",
    "python programming"               : "python",
    "python language"                  : "python",
    "machine learning ml"              : "machine learning",
    "artificial intelligence ai"       : "artificial intelligence",
    "natural language processing nlp"  : "natural language processing",
    "computer vision cv"               : "computer vision",
    "data visualization dataviz"       : "data visualization",
    "sql programming"                  : "sql",
    "mysql database"                   : "mysql",
    "data structures"                  : "data structures and algorithms",
    "algorithms"                       : "data structures and algorithms",
}

# Filler words to remove from start of skill
FILLERS = [
    "basic ",
    "basics of ",
    "advanced ",
    "good ",
    "strong ",
    "some ",
    "proficient in ",
    "knowledge of ",
    "experience in ",
    "familiar with ",
    "working knowledge of ",
    "expertise in ",
    "skilled in ",
    "understanding of ",
    "i know ",
    "i have ",
    "i can ",
]

# MAIN FUNCTION — Extract skills from raw text
# Called by FastAPI during ML pipeline 

def extract_skills(raw_text: str) -> List[str]:
    """
    Input  → raw text string from user form
             "I know Python, SQL and basic Machine Learning"

    Output → clean normalized skill list
             ["python", "sql", "machine learning"]
    """

    # Step 1: Split by comma and newline
    parts = []
    for chunk in raw_text.split("\n"):
        for part in chunk.split(","):
            parts.append(part.strip())

    # Step 2: Clean each part
    skills = []
    for part in parts:
        skill = part.lower().strip()

        # Skip empty
        if not skill or len(skill) < 2:
            continue

        # Remove filler words from start
        skill = _remove_fillers(skill)

        # Skip if too short after cleaning
        if not skill or len(skill) < 2:
            continue

        skills.append(skill)

    # Step 3: Apply synonym normalization
    skills = [SYNONYM_MAP.get(s, s) for s in skills]

    # Step 4: Remove duplicates, keep order
    seen  = set()
    final = []
    for s in skills:
        if s not in seen and len(s) > 1:
            seen.add(s)
            final.append(s)

    return final

# HELPER: Remove filler words from start

def _remove_fillers(skill: str) -> str:
    """
    Removes filler words from the beginning of a skill string
    Uses simple startswith — no regex
    """
    for filler in FILLERS:
        if skill.startswith(filler):
            skill = skill[len(filler):].strip()
            break
    return skill

# TEST — Run directly to test
# uv run python skill_extractor.py

if __name__ == "__main__":

    print("=" * 55)
    print("SKILL EXTRACTOR TEST")
    print("=" * 55)

    test_inputs = [
        "Python, SQL, Pandas, basic ML",
        "I know JavaScript, React and Node.js",
        "java, spring boot, microservices, docker, kubernetes",
        "deep learning, tensorflow, computer vision, python",
        "proficient in Python, knowledge of SQL, experience in ML",
        "basic statistics, some data visualization, familiar with pandas",
    ]

    for text in test_inputs:
        skills = extract_skills(text)
        print(f"\nInput  : {text}")
        print(f"Output : {skills}")

    print("\nDone!")

