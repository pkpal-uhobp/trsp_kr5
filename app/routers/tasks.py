from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependencies import get_current_user, get_storage
from app.schemas import TaskCreate, TaskOut, TaskStatus, TaskStatusUpdate
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])

CurrentUser = Annotated[dict[str, int | str], Depends(get_current_user)]
Storage = Annotated[TaskStorage, Depends(get_storage)]


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, current_user: CurrentUser, storage: Storage) -> dict:
    return storage.create_task(payload, owner_id=int(current_user["id"]))


@router.get("", response_model=list[TaskOut])
def list_tasks(
    current_user: CurrentUser,
    storage: Storage,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    min_priority: Annotated[int | None, Query(ge=1, le=5)] = None,
) -> list[dict]:
    return storage.list_tasks(
        owner_id=int(current_user["id"]),
        status=task_status,
        min_priority=min_priority,
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, current_user: CurrentUser, storage: Storage) -> dict:
    task = storage.get_task(task_id)
    if task is None or task["owner_id"] != int(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    current_user: CurrentUser,
    storage: Storage,
) -> dict:
    task = storage.get_task(task_id)
    if task is None or task["owner_id"] != int(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated = storage.update_status(task_id, payload.status)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user: CurrentUser, storage: Storage) -> Response:
    task = storage.get_task(task_id)
    if task is None or task["owner_id"] != int(current_user["id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    storage.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
