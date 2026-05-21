from __future__ import annotations

from collections import Counter
from copy import deepcopy
from threading import Lock
from typing import Any

from app.schemas import TaskCreate, TaskStatus


class TaskStorage:
    """Простое in-memory хранилище задач для учебных интеграционных тестов."""

    def __init__(self) -> None:
        self._tasks: dict[int, dict[str, Any]] = {}
        self._next_id = 1
        self._lock = Lock()

    def clear(self) -> None:
        with self._lock:
            self._tasks.clear()
            self._next_id = 1

    def create_task(self, data: TaskCreate, owner_id: int) -> dict[str, Any]:
        with self._lock:
            task_id = self._next_id
            self._next_id += 1
            task = data.model_dump(mode="json")
            task.update({"id": task_id, "owner_id": owner_id})
            self._tasks[task_id] = task
            return deepcopy(task)

    def list_tasks(
        self,
        *,
        owner_id: int | None = None,
        status: TaskStatus | None = None,
        min_priority: int | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            result = list(self._tasks.values())
            if owner_id is not None:
                result = [task for task in result if task["owner_id"] == owner_id]
            if status is not None:
                result = [task for task in result if task["status"] == status.value]
            if min_priority is not None:
                result = [task for task in result if task["priority"] >= min_priority]
            return deepcopy(sorted(result, key=lambda task: task["id"]))

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            return deepcopy(task) if task is not None else None

    def update_status(self, task_id: int, status: TaskStatus) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            task["status"] = status.value
            return deepcopy(task)

    def delete_task(self, task_id: int) -> bool:
        with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            return True

    def stats(self) -> dict[str, Any]:
        with self._lock:
            by_status = Counter(task["status"] for task in self._tasks.values())
            return {
                "total_tasks": len(self._tasks),
                "by_status": {
                    "todo": by_status.get("todo", 0),
                    "in_progress": by_status.get("in_progress", 0),
                    "done": by_status.get("done", 0),
                },
            }


default_storage = TaskStorage()
