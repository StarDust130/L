from typing import Literal

from pydantic import BaseModel


class ExtractedResume(BaseModel):
    filename: str
    file_type: Literal["pdf", "docx", "txt"]
    text: str
    character_count: int
