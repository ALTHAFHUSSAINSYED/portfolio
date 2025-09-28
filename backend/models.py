from pydantic import BaseModel
from typing import Optional

class ChatbotQuery(BaseModel):
    message: str
    session_id: Optional[str] = None