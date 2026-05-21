from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.todo
    priority: int = Field(..., ge=1, le=5)


class TaskCreate(TaskBase):
    pass


class TaskOut(TaskBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class UserOut(BaseModel):
    id: int
    role: str


class RoomUsersOut(BaseModel):
    room_id: str
    users: list[str]
