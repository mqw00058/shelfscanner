import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

UPLOAD_DIR = BASE_DIR / "uploads"
CROPS_DIR = BASE_DIR / "crops"
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR.mkdir(exist_ok=True)
CROPS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

PRODUCTS_FILE = DATA_DIR / "products.json"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

MAX_FRAMES = 8              # more frames = more products captured
MAX_UPLOAD_SIZE_MB = 200
CROP_MIN_AREA = 3000
VISION_MODEL = "claude-sonnet-4-20250514"

# Frame quality thresholds
BLUR_THRESHOLD = 80.0       # Laplacian variance below this = blurry
MOTION_BLUR_THRESHOLD = 50.0  # stricter threshold for motion blur detection
MIN_SHARPNESS_SCORE = 60.0  # minimum acceptable sharpness after all checks
