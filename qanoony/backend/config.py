from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

EMPLOYMENT_CHROMA_DIR = BASE_DIR / "data" / "employment" / "chroma_db"
COMPANY_FORMATION_CHROMA_DIR = BASE_DIR / "data" / "company_formation" / "chroma_db"
COMPANY_FORMATION_RAW_DIR = BASE_DIR / "data" / "company_formation" / "raw"
COMPANY_FORMATION_CLEANED_DIR = BASE_DIR / "data" / "company_formation" / "cleaned"
COMPANY_FORMATION_CHUNKS_DIR = BASE_DIR / "data" / "company_formation" / "chunks"
