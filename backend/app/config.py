import os
from pathlib import Path

# Load backend/.env into os.environ so GROQ_* and other secrets work without manual export.
# Note: your interactive shell does not read .env — `echo $GROQ_API_KEY` stays blank unless you export it.
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
try:
    from dotenv import load_dotenv

    load_dotenv(_BACKEND_ROOT / ".env")
except ImportError:
    pass

ROOT_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT_DIR / "goadataset.csv"
GOA_GEOJSON_PATH = ROOT_DIR / "goa.geojson"
GENERATED_DIR = ROOT_DIR / "backend" / "generated"
MAPS_DIR = GENERATED_DIR / "maps"
EXPORTS_DIR = GENERATED_DIR / "exports"
OSRM_BASE_URL = "http://localhost:5000"
DESCRIPTION_DATA_DIR = ROOT_DIR / "Description_data"
MODAL_NARRATION_URL = os.getenv("MODAL_NARRATION_URL", "").strip()

# Groq (OpenAI-compatible chat) for one-shot fitness profile resolution — optional.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1").strip()
