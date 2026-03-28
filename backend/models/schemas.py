from pydantic import BaseModel


class DetectedProduct(BaseModel):
    name: str
    price: float | None = None
    unit: str | None = None
    desc: str | None = None
    shelf: str | None = None
    badge: str | None = None
    image: str | None = None
    imageUrl: str | None = None
    emoji: str = "📦"
    category: str | None = None
    bbox: list[int] | None = None


class AnalysisResponse(BaseModel):
    store: str
    products: list[DetectedProduct]
    frames_analyzed: int
    processing_time_seconds: float
