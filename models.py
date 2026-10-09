from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ProductOut(BaseModel):
    id: int
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    fetched_at: str

class SyncSummary(BaseModel):
    status: str
    items_ingested: int
    source_pages: int
    duration_ms: int
