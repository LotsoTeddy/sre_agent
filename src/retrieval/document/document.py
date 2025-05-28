from pydantic import BaseModel
from typing import Optional


class Document(BaseModel):
    page_content: str
    vector: Optional[list[float]] = None
    metadata: dict = {}
