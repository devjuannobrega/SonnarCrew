"""
Configuration package for Code Analysis Agent
"""

import os
from pathlib import Path

# Configuration paths
CONFIG_DIR = Path(__file__).parent
AGENTS_CONFIG_PATH = CONFIG_DIR / "agents.yaml"
TASKS_CONFIG_PATH = CONFIG_DIR / "tasks.yaml"

# Environment variables with defaults
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/code_analysis_db"
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Application settings
MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "10000"))
ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT_SECONDS", "30"))
MAX_SUGGESTIONS = int(os.getenv("MAX_SUGGESTIONS", "50"))

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# CrewAI settings
CREW_MEMORY_ENABLED = os.getenv("CREW_MEMORY_ENABLED", "True").lower() == "true"
CREW_VERBOSE = os.getenv("CREW_VERBOSE", "True").lower() == "true"

__all__ = [
    "CONFIG_DIR",
    "AGENTS_CONFIG_PATH",
    "TASKS_CONFIG_PATH",
    "DATABASE_URL",
    "REDIS_URL",
    "LOG_LEVEL",
    "ENVIRONMENT",
    "DEBUG",
    "MAX_CODE_LENGTH",
    "ANALYSIS_TIMEOUT",
    "MAX_SUGGESTIONS",
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "CREW_MEMORY_ENABLED",
    "CREW_VERBOSE"
]