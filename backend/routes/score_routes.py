"""Score entry routes — last 5 scores, 1 per date, Stableford 1..45."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user
from models import ScoreCreate, ScoreUpdate
from services import db as sdb

router = APIRouter(prefix="/scores", tags=["scores"])

MAX_SCORES = 5


@router.get("")
async def list_my_scores(user: dict = Depends(get_current_user)):
    return await sdb.select_many(
        "scores", {"user_id": user["id"]},
        order_by="date", ascending=False, limit=50,
    )


@router.post("")
async def create_score(payload: ScoreCreate, user: dict = Depends(get_current_user)):
    try:
        datetime.strptime(payload.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "date must be YYYY-MM-DD")

    existing = await sdb.select_one("scores", {"user_id": user["id"], "date": payload.date})
    if existing:
        raise HTTPException(400, "Score for this date already exists. Edit or delete it.")

    doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "value": int(payload.value),
        "date": payload.date,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    created = await sdb.insert_one("scores", doc)

    # Evict oldest if > MAX_SCORES
    all_scores = await sdb.select_many(
        "scores", {"user_id": user["id"]},
        order_by="date", ascending=False, limit=100,
    )
    if len(all_scores) > MAX_SCORES:
        for s in all_scores[MAX_SCORES:]:
            await sdb.delete_by("scores", {"id": s["id"]})

    return created


@router.patch("/{score_id}")
async def update_score(score_id: str, payload: ScoreUpdate, user: dict = Depends(get_current_user)):
    existing = await sdb.select_one("scores", {"id": score_id, "user_id": user["id"]})
    if not existing:
        raise HTTPException(404, "Not found")
    return await sdb.update_by("scores", {"id": score_id}, {"value": int(payload.value)})


@router.delete("/{score_id}")
async def delete_score(score_id: str, user: dict = Depends(get_current_user)):
    existing = await sdb.select_one("scores", {"id": score_id, "user_id": user["id"]})
    if not existing:
        raise HTTPException(404, "Not found")
    await sdb.delete_by("scores", {"id": score_id})
    return {"ok": True}
