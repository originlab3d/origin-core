import os
from dataclasses import dataclass

@dataclass
class Config: 
    # API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Modèle IA
    MODEL_NAME: str = "gemini-2.5-flash-lite" #gemini-1.5-flash  gemini-2.5-flash-lite
    TEMPERATURE: float = 0.5 
    MAX_TOKENS: int = 800
    
    # Mémoire (tokens optimisés)
    IMMEDIATE_MEMORY: int = 6
    WORKING_MEMORY: int = 4
    EPISODIC_MEMORY: int = 8
    SEMANTIC_MEMORY: int = 3
    
    # Résumés
    SUMMARY_THRESHOLD: int = 5
    KEEP_AFTER_SUMMARY: int = 2
    
    # Affinité
    AFFINITY_MIN: int = -20
    AFFINITY_MAX: int = 20
    
    # Performance
    DB_POOL_MIN: int = 2 
    DB_POOL_MAX: int = 8
    CACHE_TTL: int = 300

config = Config()