from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(
    current_user: Annotated[dict[str, int | str], Depends(get_current_user)],
) -> dict[str, int | str]:
    return current_user


@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int) -> dict[str, int | str]:
    return {"id": user_id, "role": "user"}
