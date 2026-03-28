from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import CROPS_DIR, PROJECT_DIR
from backend.routers.upload import router as upload_router

app = FastAPI(title="Shelf Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)

# Serve cropped product images
app.mount("/api/crops", StaticFiles(directory=str(CROPS_DIR)), name="crops")

# Serve frontend static files (must be last)
app.mount("/", StaticFiles(directory=str(PROJECT_DIR), html=True), name="frontend")
