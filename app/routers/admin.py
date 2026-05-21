from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.dependencies import get_storage, require_admin
from app.storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])

AdminUser = Annotated[dict[str, int | str], Depends(require_admin)]
Storage = Annotated[TaskStorage, Depends(get_storage)]


@router.get("/stats")
def get_stats(_: AdminUser, storage: Storage) -> dict:
    return storage.stats()


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_any_task(task_id: int, _: AdminUser, storage: Storage) -> Response:
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
