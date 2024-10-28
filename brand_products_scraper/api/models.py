# api/models.py
from pydantic import BaseModel
from typing import List, Optional

class ScraperRequest(BaseModel):
    brand: str
    categories: Optional[List[str]] = None
    max_pages: Optional[int] = None