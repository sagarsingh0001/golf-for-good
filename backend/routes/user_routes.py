"""User profile routes."""
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from models import CharitySelection
from services import db as sdb

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me/charity")
async def update_charity(payload: CharitySelection, user: dict = Depends(get_current_user)):
    if not await sdb.select_one("charities", {"id": payload.charity_id}):
        raise HTTPException(status_code=400, detail="Invalid charity")
    updated = await sdb.update_by(
        "users",
        {"id": user["id"]},
        {"charity_id": payload.charity_id, "charity_percentage": float(payload.charity_percentage)},
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {k: v for k, v in updated.items() if k != "password_hash"}
