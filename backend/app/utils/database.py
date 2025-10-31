import os
import yaml
import urllib.parse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator, Optional, Dict, Any

# Load environment variables
load_dotenv()

# --- Directory setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")       


def load_config(section: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file based on APP_ENV.

    Args:
        section (Optional[str]): Section name (e.g., "LOCAL_DATABASE").
    Returns:
        Dict[str, Any]: Config dictionary or subsection.
    """
    env = os.getenv("APP_ENV", "LOCAL").upper()
    config_file = os.path.join(CONFIG_DIR, f"{env.lower()}.yml")

    # Fallback: root/local.yml
    if not os.path.exists(config_file):
        config_file = os.path.join(PROJECT_ROOT, "local.yml")

    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r") as f:
        config: Dict[str, Any] = yaml.safe_load(f) or {}

    if section:
        if section not in config:
            raise KeyError(f"Expected section '{section}' in {config_file}, found {list(config.keys())}")
        return config[section]

    return config


def build_base_url(config: Dict[str, Any]) -> str:
    """
    Build SQLAlchemy connection URL without specifying database.
    """
    user = config["USER_NAME"]
    password = urllib.parse.quote_plus(config["PASSWORD"])
    host = config["HOST"]
    port = config["PORT"]
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/"


def build_database_url(config: Dict[str, Any]) -> str:
    """
    Build SQLAlchemy connection URL including the database name.
    """
    return build_base_url(config) + config["DATABASE_NAME"]


def create_db_engine():
    """
    Create PostgreSQL database engine using psycopg2.
    Ensures the database exists before connecting.
    """
    db_conf = load_config("DATABASE")

    # Step 1: Connect without database name
    base_engine = create_engine(build_base_url(db_conf), isolation_level="AUTOCOMMIT")

    # Step 2: Create DB if missing
    db_name = db_conf["DATABASE_NAME"]
    with base_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
        if not result.scalar():
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))

    # Step 3: Connect to actual database
    return create_engine(build_database_url(db_conf), pool_pre_ping=True)


# --- Initialize Engine, Session, Base ---
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes.
    Provides and closes SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
