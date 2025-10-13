from pydantic import BaseModel
from typing import Optional

class MailRequest(BaseModel):
    sender: str
    subject: str
    body: str
    to: str
    cc: Optional[str] = None
