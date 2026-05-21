from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class RoomManager:
    """Менеджер WebSocket-комнат и активных подключений."""

    def __init__(self) -> None:
        self._rooms: dict[str, dict[str, set[WebSocket]]] = defaultdict(lambda: defaultdict(set))

    async def connect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._rooms[room_id][username].add(websocket)

    def disconnect(self, room_id: str, username: str, websocket: WebSocket) -> None:
        users = self._rooms.get(room_id)
        if not users:
            return

        connections = users.get(username)
        if connections:
            connections.discard(websocket)
            if not connections:
                users.pop(username, None)

        if not users:
            self._rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, payload: dict[str, Any]) -> None:
        users = self._rooms.get(room_id, {})
        websockets = [websocket for connections in users.values() for websocket in connections]
        for websocket in websockets:
            await websocket.send_json(payload)

    def get_users(self, room_id: str) -> list[str]:
        return sorted(self._rooms.get(room_id, {}).keys())

    def clear(self) -> None:
        self._rooms.clear()


room_manager = RoomManager()
