"""Charity routes."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from auth import admin_required
from models import CharityCreate, CharityUpdate

router = APIRouter(prefix="/charities", tags=["charities"])


@router.get("")
async def list_charities(q: Optional[str] = None, category: Optional[str] = None):
    from server import db
    filt = {}
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    if category and category != "all":
        filt["category"] = category
    items = await db.charities.find(filt, {"_id": 0}).to_list(500)
    return items


@router.get("/featured")
async def featured():
    from server import db
    return await db.charities.find({"featured": True}, {"_id": 0}).to_list(10)


@router.get("/{charity_id}")
async def get_charity(charity_id: str):
    from server import db
    c = await db.charities.find_one({"id": charity_id}, {"_id": 0})
    if not c:
        raise HTTPException(404, "Not found")
    return c


@router.post("", dependencies=[Depends(admin_required)])
async def create_charity(payload: CharityCreate):
    from server import db
    doc = {
        "id": str(uuid.uuid4()),
        **payload.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.charities.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.patch("/{charity_id}", dependencies=[Depends(admin_required)])
async def update_charity(charity_id: str, payload: CharityUpdate):
    from server import db
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(400, "Nothing to update")
    result = await db.charities.update_one({"id": charity_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(404, "Not found")
    return await db.charities.find_one({"id": charity_id}, {"_id": 0})


@router.delete("/{charity_id}", dependencies=[Depends(admin_required)])
async def delete_charity(charity_id: str):
    from server import db
    result = await db.charities.delete_one({"id": charity_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Not found")
    return {"ok": True}
