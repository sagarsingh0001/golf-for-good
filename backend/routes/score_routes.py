"""Score entry routes — last 5 scores, 1 per date, Stableford 1..45."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from models import ScoreCreate, ScoreUpdate

router = APIRouter(prefix="/scores", tags=["scores"])

MAX_SCORES = 5


@router.get("")
async def list_my_scores(user: dict = Depends(get_current_user)):
    from server import db
    items = await db.scores.find({"user_id": user["id"]}, {"_id": 0}).sort("date", -1).to_list(50)
    return items


@router.post("")
async def create_score(payload: ScoreCreate, user: dict = Depends(get_current_user)):
    from server import db
    # Validate date
    try:
        datetime.strptime(payload.date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, "date must be YYYY-MM-DD")

    # Ensure unique per date
    existing = await db.scores.find_one({"user_id": user["id"], "date": payload.date})
    if existing:
        raise HTTPException(400, "Score for this date already exists. Edit or delete it.")

    doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "value": payload.value,
        "date": payload.date,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.scores.insert_one(doc)

    # Keep only latest 5 (by date desc)
    all_scores = await db.scores.find({"user_id": user["id"]}, {"_id": 0}).sort("date", -1).to_list(100)
    if len(all_scores) > MAX_SCORES:
        to_remove = all_scores[MAX_SCORES:]
        ids = [s["id"] for s in to_remove]
        await db.scores.delete_many({"id": {"$in": ids}})

    return {k: v for k, v in doc.items() if k != "_id"}


@router.patch("/{score_id}")
async def update_score(score_id: str, payload: ScoreUpdate, user: dict = Depends(get_current_user)):
    from server import db
    res = await db.scores.update_one(
        {"id": score_id, "user_id": user["id"]},
        {"$set": {"value": payload.value}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "Not found")
    return await db.scores.find_one({"id": score_id}, {"_id": 0})


@router.delete("/{score_id}")
async def delete_score(score_id: str, user: dict = Depends(get_current_user)):
    from server import db
    res = await db.scores.delete_one({"id": score_id, "user_id": user["id"]})
    if res.deleted_count == 0:
        raise HTTPException(404, "Not found")
    return {"ok": True}
