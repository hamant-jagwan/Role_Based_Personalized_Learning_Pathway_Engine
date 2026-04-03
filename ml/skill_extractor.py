# ml/skill_extractor.py
# ML Pipeline — Skill Extractor
# Stage 1: Uses JobBERT (jjzha/jobbert-base-cased) for NER-based skill extraction
# Falls back to rule-based splitter if model is unavailable

from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# ── Synonym normalisation map ──────────────────────────────────────────────────
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

# ── Filler phrases to strip from skill starts ──────────────────────────────────
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

# ── JobBERT model name ─────────────────────────────────────────────────────────
# jjzha/jobbert-base-cased is fine-tuned on job postings for skill/knowledge/
# experience NER. It tags tokens with B-SKILL, I-SKILL, B-KNOWLEDGE, etc.
JOBBERT_MODEL = "jjzha/jobbert-base-cased"

# ── Module-level pipeline — loaded once, reused across all requests ────────────
# Set to None initially; _load_model() is called lazily on first use
# (or eagerly from main.py startup — see note at bottom of file)
_ner_pipeline = None


def _load_model() -> Optional[object]:
    """
    Load the JobBERT NER pipeline. Returns the pipeline on success, None on failure.
    Failure is non-fatal — the rule-based fallback takes over automatically.
    """
    global _ner_pipeline
    if _ner_pipeline is not None:
        return _ner_pipeline

    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

        logger.info("Loading JobBERT model: %s", JOBBERT_MODEL)

        tokenizer = AutoTokenizer.from_pretrained(JOBBERT_MODEL)
        model     = AutoModelForTokenClassification.from_pretrained(JOBBERT_MODEL)

        # aggregation_strategy="simple" merges B-/I- tokens into full spans
        _ner_pipeline = pipeline(
            task                  = "ner",
            model                 = model,
            tokenizer             = tokenizer,
            aggregation_strategy  = "simple",
        )

        logger.info("JobBERT loaded successfully")
        return _ner_pipeline

    except Exception as e:
        logger.warning("JobBERT failed to load (%s). Using rule-based fallback.", e)
        return None




def extract_skills(raw_text: str) -> List[str]:
    """
    Extract and normalise skills from free-form user text.

    Input:
        raw_text → "I know Python, SQL and basic Machine Learning"

    Output:
        ["python", "sql", "machine learning"]

    Strategy:
        1. Try JobBERT NER  → pulls skill spans from the sentence
        2. If model unavailable → fall back to comma/newline split (old behaviour)
        3. In both cases: strip fillers, apply synonym map, deduplicate
    """
    if not raw_text or not raw_text.strip():
        return []

    pipe = _load_model()

    if pipe is not None:
        raw_skills = _extract_with_jobbert(pipe, raw_text)

        # If JobBERT found nothing (e.g. purely comma-listed input with no context),
        # blend in the rule-based results so we never return empty-handed.
        if not raw_skills:
            logger.debug("JobBERT returned no spans — blending rule-based results")
            raw_skills = _extract_rule_based(raw_text)
    else:
        raw_skills = _extract_rule_based(raw_text)

    return _normalise(raw_skills)


# ── STRATEGY 1 — JobBERT NER ───────────────────────────────────────────────────

def _extract_with_jobbert(pipe, raw_text: str) -> List[str]:
    """
    Run the JobBERT NER pipeline and return skill span strings.

    JobBERT entity labels used:
        B-SKILL / I-SKILL          → direct skill mentions
        B-KNOWLEDGE / I-KNOWLEDGE  → domain knowledge (treated as skills here)

    Spans shorter than 2 characters are discarded.
    """
    try:
        # JobBERT has a 512-token limit; truncate very long inputs
        text = raw_text[:2000]

        entities = pipe(text)
        skills   = []

        for ent in entities:
            label = ent.get("entity_group", "").upper()

            # Accept SKILL and KNOWLEDGE entity groups
            if "SKILL" not in label and "KNOWLEDGE" not in label:
                continue

            span = ent.get("word", "").strip()

            # Remove subword artefacts that HuggingFace sometimes leaves
            # (e.g. "##ing" fragments)
            if span.startswith("##") or len(span) < 2:
                continue

            skills.append(span)

        return skills

    except Exception as e:
        logger.warning("JobBERT inference failed: %s", e)
        return []


# ── STRATEGY 2 — Rule-based fallback (original logic, unchanged) ───────────────

def _extract_rule_based(raw_text: str) -> List[str]:
    """
    Original comma/newline splitter. Used when JobBERT is unavailable
    or returns no spans.
    """
    parts = []
    for chunk in raw_text.split("\n"):
        for part in chunk.split(","):
            parts.append(part.strip())

    skills = []
    for part in parts:
        skill = part.lower().strip()
        if not skill or len(skill) < 2:
            continue
        skill = _remove_fillers(skill)
        if not skill or len(skill) < 2:
            continue
        skills.append(skill)

    return skills


# ── SHARED POST-PROCESSING ─────────────────────────────────────────────────────

def _normalise(raw_skills: List[str]) -> List[str]:
    """
    Apply filler removal, lowercasing, synonym mapping, and deduplication.
    Works on output from both strategies.
    """
    cleaned = []
    for s in raw_skills:
        skill = s.lower().strip()
        if not skill or len(skill) < 2:
            continue
        skill = _remove_fillers(skill)
        if not skill or len(skill) < 2:
            continue
        cleaned.append(skill)

    # Synonym normalisation
    cleaned = [SYNONYM_MAP.get(s, s) for s in cleaned]

    # Deduplicate, preserve order
    seen  = set()
    final = []
    for s in cleaned:
        if s not in seen and len(s) > 1:
            seen.add(s)
            final.append(s)

    return final


def _remove_fillers(skill: str) -> str:
    """Strip leading filler phrases (e.g. 'proficient in', 'knowledge of')."""
    for filler in FILLERS:
        if skill.startswith(filler):
            return skill[len(filler):].strip()
    return skill


# ── EAGER LOAD HELPER ──────────────────────────────────────────────────────────
# Call this from main.py startup so the model is warm before the first request.
# See main.py changes below.

def warmup():
    """Pre-load JobBERT at application startup. Safe to call multiple times."""
    _load_model()


# ── TEST — uv run python skill_extractor.py ────────────────────────────────────

if __name__ == "__main__":

    print("=" * 60)
    print("SKILL EXTRACTOR TEST  —  JobBERT + rule-based fallback")
    print("=" * 60)

    test_inputs = [
        "Python, SQL, Pandas, basic ML",
        "I know JavaScript, React and Node.js",
        "java, spring boot, microservices, docker, kubernetes",
        "deep learning, tensorflow, computer vision, python",
        "proficient in Python, knowledge of SQL, experience in ML",
        "basic statistics, some data visualization, familiar with pandas",
        # Sentences that benefit most from NER
        "I have 3 years of experience working with PyTorch and building REST APIs",
        "Skilled in cloud infrastructure using AWS and Terraform",
    ]

    for text in test_inputs:
        skills = extract_skills(text)
        print(f"\nInput  : {text}")
        print(f"Output : {skills}")

    print("\nDone!")