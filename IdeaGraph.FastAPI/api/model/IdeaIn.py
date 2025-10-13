from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import datetime, date

class IdeaIn(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = []
    status: str = "New"
