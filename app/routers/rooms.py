from typing import Annotated

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from app.room_manager import room_manager
from app.schemas import RoomUsersOut

router = APIRouter(tags=["rooms"])


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(
    websocket: WebSocket,
    room_id: str,
    username: Annotated[str | None, Query()] = None,
) -> None:
    if username is None or not username.strip():
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    clean_username = username.strip()
    await room_manager.connect(room_id, clean_username, websocket)
    await room_manager.broadcast(
        room_id,
        {
            "type": "join",
            "room_id": room_id,
            "username": clean_username,
            "users": room_manager.get_users(room_id),
        },
    )

    try:
        while True:
            payload = await websocket.receive_json()
            if payload.get("type") != "message":
                await websocket.send_json({"type": "error", "detail": "Unsupported message type"})
                continue

            text = str(payload.get("text", ""))
            if len(text) > 300:
                await websocket.send_json({"type": "error", "detail": "Message is too long"})
                continue

            await room_manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": clean_username,
                    "text": text,
                },
            )
    except WebSocketDisconnect:
        room_manager.disconnect(room_id, clean_username, websocket)


@router.get("/rooms/{room_id}/users", response_model=RoomUsersOut)
def get_room_users(room_id: str) -> dict[str, object]:
    return {"room_id": room_id, "users": room_manager.get_users(room_id)}
