from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import datetime, date

class FileContentResponse(BaseModel):
    path: str
    content: str
