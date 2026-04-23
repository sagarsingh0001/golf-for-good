"""Charity routes."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from auth import admin_required
from models import CharityCreate, CharityUpdate
from services import db as sdb

router = APIRouter(prefix="/charities", tags=["charities"])


@router.get("")
async def list_charities(q: Optional[str] = None, category: Optional[str] = None):
    # Build filter: if q present, use ilike on name; else fetch all (optionally filtered by category)
    if q:
        extra = {"category": category} if category and category != "all" else None
        return await sdb.search_ilike("charities", "name", f"%{q}%", extra_filters=extra)
    filt = {}
    if category and category != "all":
        filt["category"] = category
    return await sdb.select_many("charities", filt, order_by="created_at", ascending=False, limit=500)


@router.get("/featured")
async def featured():
    return await sdb.select_many("charities", {"featured": True}, limit=10)


@router.get("/{charity_id}")
async def get_charity(charity_id: str):
    c = await sdb.select_one("charities", {"id": charity_id})
    if not c:
        raise HTTPException(404, "Not found")
    return c


@router.post("", dependencies=[Depends(admin_required)])
async def create_charity(payload: CharityCreate):
    doc = {
        "id": str(uuid.uuid4()),
        **payload.model_dump(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return await sdb.insert_one("charities", doc)


@router.patch("/{charity_id}", dependencies=[Depends(admin_required)])
async def update_charity(charity_id: str, payload: CharityUpdate):
    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not update:
        raise HTTPException(400, "Nothing to update")
    updated = await sdb.update_by("charities", {"id": charity_id}, update)
    if not updated:
        raise HTTPException(404, "Not found")
    return updated


@router.delete("/{charity_id}", dependencies=[Depends(admin_required)])
async def delete_charity(charity_id: str):
    n = await sdb.delete_by("charities", {"id": charity_id})
    if n == 0:
        raise HTTPException(404, "Not found")
    return {"ok": True}
