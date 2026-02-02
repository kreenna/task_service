from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskCreate(BaseModel):
    payload: str


class TaskResponse(TaskCreate):
    id: int
    status: str
    result: Optional[str] = None
    created_at: datetime
    updated_at: datetime
