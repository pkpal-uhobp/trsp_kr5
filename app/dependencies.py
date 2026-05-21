from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.storage import TaskStorage, default_storage


def get_current_user(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
    x_user_role: Annotated[str, Header(alias="X-User-Role")] = "user",
) -> dict[str, int | str]:
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required",
        )

    try:
        user_id = int(x_user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id must be an integer",
        ) from None

    role = (x_user_role or "user").strip() or "user"
    return {"id": user_id, "role": role}


def require_admin(
    current_user: Annotated[dict[str, int | str], Depends(get_current_user)],
) -> dict[str, int | str]:
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role is required",
        )
    return current_user


def get_storage() -> TaskStorage:
    return default_storage
