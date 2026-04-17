#   1. load_graph():  loads role_skill_mapping.csv into Neo4j
#   2. get_role_requirements() — queries Neo4j for a given role

from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

NEO4J_URI=neo4j+s://2b139927.databases.neo4j.io
NEO4J_USERNAME=2b139927
NEO4J_PASSWORD=ZHR-kTvs90eJj7nRBTtPIlm3E6NkuQmhidb_hKjlQ3Q

# Neo4j connection 
NEO4J_URI      = os.getenv("NEO4J_URI",      "neo4j+s://2b139927.databases.neo4j.io")
NEO4J_USER     = os.getenv("NEO4J_USER",     "2b139927")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "ZHR-kTvs90eJj7nRBTtPIlm3E6NkuQmhidb_hKjlQ3Q")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Path to cleaned dataset 
MAPPING_PATH = "../data/cleaned/role_skill_mapping.csv"


# FUNCTION 1: Load CSV into Neo4j
# Run this ONCE to populate the graph

def load_graph():
    df = pd.read_csv(MAPPING_PATH)
    print(f"Loading {len(df)} role-skill pairs into Neo4j...")

    with driver.session() as session:

        # Clear existing data first
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing graph data")

        # Create nodes and relationships for each row
        for _, row in df.iterrows():
            session.run(
                """
                MERGE (r:Role  {name: $role})
                MERGE (s:Skill {name: $skill})
                MERGE (r)-[rel:REQUIRES]->(s)
                SET rel.importance = $importance
                """,
                role       = row["role_name"],
                skill      = row["required_skill"],
                importance = float(row["importance_score"])
            )

    print("Graph loaded successfully!")
    print(f"Roles loaded : {df['role_name'].nunique()}")
    print(f"Skills loaded: {df['required_skill'].nunique()}")

# FUNCTION 2 : Query role requirements
# Called by FastAPI during ML pipeline 

def get_role_requirements(role_name: str) -> list:
    """
    Input  → role_name: "Data Scientist"
    Output → list of required skills sorted by importance
             ["python", "machine learning", "sql", ...]
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (r:Role {name: $role})-[rel:REQUIRES]->(s:Skill)
            RETURN s.name AS skill, rel.importance AS importance
            ORDER BY rel.importance DESC
            """,
            role=role_name
        )
        skills = [record["skill"] for record in result]

    return skills

# FUNCTION 3 — Get importance scores
# Returns skills with their importance scores
# Used by Gap Analysis for weighted gap score

def get_role_requirements_with_importance(role_name: str) -> dict:
    """
    Input  → role_name: "Data Scientist"
    Output → dict of skill → importance score
             {"python": 0.95, "machine learning": 0.80, ...}
    """
    with driver.session() as session:
        result = session.run(
            """
            MATCH (r:Role {name: $role})-[rel:REQUIRES]->(s:Skill)
            RETURN s.name AS skill, rel.importance AS importance
            ORDER BY rel.importance DESC
            """,
            role=role_name
        )
        skills = {record["skill"]: record["importance"] for record in result}

    return skills

# FUNCTION 4: Get all available roles
# Used to validate role names in FastAPI

def get_all_roles() -> list:
    """
    Returns all role names stored in Neo4j
    """
    with driver.session() as session:
        result = session.run("MATCH (r:Role) RETURN r.name AS role ORDER BY r.name")
        roles = [record["role"] for record in result]
    return roles


# TEST — Run this file directly to test
# python knowledge_graph.py

if __name__ == "__main__":

    # Step 1: Load CSV into Neo4j
    print("=" * 50)
    print("STEP 1 — Loading graph...")
    print("=" * 50)
    load_graph()

    # Step 2: Test query
    print("\n" + "=" * 50)
    print("STEP 2 — Testing query...")
    print("=" * 50)

    test_role = "Data Scientist"
    skills = get_role_requirements(test_role)
    print(f"\nRequired skills for '{test_role}':")
    for i, skill in enumerate(skills, 1):
        print(f"  {i:2}. {skill}")

    # Step 3: Test with importance scores
    print("\n" + "=" * 50)
    print("STEP 3 — Testing with importance scores...")
    print("=" * 50)
    skills_with_scores = get_role_requirements_with_importance(test_role)
    print(f"\nSkill importance scores for '{test_role}':")
    for skill, score in list(skills_with_scores.items())[:10]:
        bar = "█" * int(score * 20)
        print(f"  {skill:<30} {score:.2f}  {bar}")

    # Step 4: All roles
    print("\n" + "=" * 50)
    print("STEP 4 — All roles in graph:")
    print("=" * 50)
    all_roles = get_all_roles()
    for role in all_roles:
        print(f"  - {role}")

    driver.close()
    print("\nDone!")


