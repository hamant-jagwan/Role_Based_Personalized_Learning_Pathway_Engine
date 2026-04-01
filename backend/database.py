from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os

# Load environment variables from .env file 
load_dotenv()

# Database URL 
# Format: postgresql://username:password@host:port/database_name
# Values come from your .env file
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/rbplpe_database"
)

# Engine
# Engine = the actual connection to PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True      # echo=True prints every SQL query to terminal (good for debugging)
)

# Session 
# Session = a conversation with the database
# Each request gets its own session, closes when done
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base
# All your table classes (models.py) will inherit from this Base
Base = declarative_base()

# Dependency function 
# FastAPI will call this for every request that needs DB access
# It opens a session, gives it to the route, then closes it automatically
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

NEO4J_URI      = os.getenv("NEO4J_URI",     "bolt://127.0.0.1:7687")
NEO4J_USER     = os.getenv("NEO4J_USER",    "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD","password")

neo4j_driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)

def get_neo4j():
    return neo4j_driver

if __name__ == "__main__":
    # Test PostgreSQL
    try:
        with engine.connect() as conn:
            print("✅ PostgreSQL Connected!")
    except Exception as e:
        print(f"❌ PostgreSQL Failed: {e}")

    # Test Neo4j
    try:
        with neo4j_driver.session() as session:
            result = session.run("RETURN 'Neo4j Connected!' AS message")
            print(result.single()["message"])
    except Exception as e:
        print(f"❌ Neo4j Failed: {e}")