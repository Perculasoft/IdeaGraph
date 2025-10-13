from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import datetime, date

class MailRequest(BaseModel):
    sender: str
    subject: str
    body: str
    to: str
    cc: Optional[str] = None