"""User profile routes."""
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from models import CharitySelection

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/me/charity")
async def update_charity(payload: CharitySelection, user: dict = Depends(get_current_user)):
    from server import db
    c = await db.charities.find_one({"id": payload.charity_id})
    if not c:
        raise HTTPException(status_code=400, detail="Invalid charity")
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"charity_id": payload.charity_id, "charity_percentage": payload.charity_percentage}},
    )
    updated = await db.users.find_one({"id": user["id"]}, {"_id": 0, "password_hash": 0})
    return updated
