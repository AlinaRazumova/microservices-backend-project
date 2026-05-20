from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NotificationCreate(BaseModel):
    user_id: int
    task_id: Optional[int] = None
    title: str
    message: str


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    task_id: Optional[int]
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
