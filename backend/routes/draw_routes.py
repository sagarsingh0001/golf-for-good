"""Draw and prize-pool routes."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from auth import admin_required, get_current_user
from models import DrawConfig, DrawPublishRequest
from services.draw_engine import (
    random_numbers, algorithmic_numbers, count_matches, compute_prize_pool,
    MONTHLY_PRICE, YEARLY_PRICE,
)
from services.email_service import send_email, render_winner, render_draw_result

router = APIRouter(prefix="/draws", tags=["draws"])


async def _build_draw(month: str, logic_type: str):
    from server import db
    if logic_type == "algorithmic":
        docs = await db.scores.find({}, {"_id": 0, "value": 1}).to_list(10000)
        all_vals = [d["value"] for d in docs]
        nums = algorithmic_numbers(all_vals)
    else:
        nums = random_numbers()

    # Prize pool: sum of active subscriptions' contributions for this month
    active_users = await db.users.count_documents({"subscription_status": "active"})
    # Rough estimate: use mid-plan average price
    subs_total = active_users * MONTHLY_PRICE
    # Rollover from previous unclaimed 5-match
    prev = await db.draws.find_one({"status": "published", "rollover_available": {"$gt": 0}}, sort=[("month", -1)])
    rolled = prev["rollover_available"] if prev else 0.0
    pool = compute_prize_pool(subs_total, rolled)

    return {"numbers": nums, "prize_pool": pool, "active_users": active_users}


@router.post("/configure", dependencies=[Depends(admin_required)])
async def configure(payload: DrawConfig):
    """Create a draft draw for a month."""
    from server import db
    existing = await db.draws.find_one({"month": payload.month})
    if existing and existing.get("status") == "published":
        raise HTTPException(400, "Draw for this month already published")

    built = await _build_draw(payload.month, payload.logic_type)
    doc = {
        "id": str(uuid.uuid4()),
        "month": payload.month,
        "logic_type": payload.logic_type,
        "numbers": built["numbers"],
        "prize_pool": built["prize_pool"],
        "active_users": built["active_users"],
        "status": "draft",
        "rollover_available": 0.0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if existing:
        await db.draws.update_one({"month": payload.month}, {"$set": doc})
    else:
        await db.draws.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


@router.post("/simulate", dependencies=[Depends(admin_required)])
async def simulate(payload: DrawConfig):
    """Preview what a draw would look like without persisting."""
    built = await _build_draw(payload.month, payload.logic_type)
    # Calculate projected winners
    from server import db
    users = await db.users.find({"subscription_status": "active"}, {"_id": 0, "id": 1}).to_list(10000)
    tier_counts = {"tier_5": 0, "tier_4": 0, "tier_3": 0}
    for u in users:
        last5 = await db.scores.find({"user_id": u["id"]}, {"_id": 0, "value": 1}).sort("date", -1).to_list(5)
        if len(last5) < 5:
            continue
        m = count_matches([s["value"] for s in last5], built["numbers"])
        if m >= 5:
            tier_counts["tier_5"] += 1
        elif m == 4:
            tier_counts["tier_4"] += 1
        elif m == 3:
            tier_counts["tier_3"] += 1
    return {**built, "projected_winners": tier_counts}


@router.post("/publish", dependencies=[Depends(admin_required)])
async def publish(payload: DrawPublishRequest):
    """Publish draw, compute winners, persist, send emails."""
    from server import db
    draw = await db.draws.find_one({"id": payload.draw_id}, {"_id": 0})
    if not draw:
        raise HTTPException(404, "Draw not found")
    if draw["status"] == "published":
        raise HTTPException(400, "Already published")

    # Find all users and their last 5 scores
    users = await db.users.find({"subscription_status": "active", "role": "user"}, {"_id": 0}).to_list(10000)
    tier_winners = {"tier_5": [], "tier_4": [], "tier_3": []}
    for u in users:
        last5 = await db.scores.find({"user_id": u["id"]}, {"_id": 0, "value": 1, "date": 1}).sort("date", -1).to_list(5)
        if len(last5) < 5:
            continue
        m = count_matches([s["value"] for s in last5], draw["numbers"])
        if m >= 5:
            tier_winners["tier_5"].append(u)
        elif m == 4:
            tier_winners["tier_4"].append(u)
        elif m == 3:
            tier_winners["tier_3"].append(u)

    prize_pool = draw["prize_pool"]
    rollover = 0.0
    winner_docs = []
    now = datetime.now(timezone.utc).isoformat()

    for tier_key, pool_key, label in [
        ("tier_5", "tier_5", "5-Number Match"),
        ("tier_4", "tier_4", "4-Number Match"),
        ("tier_3", "tier_3", "3-Number Match"),
    ]:
        winners = tier_winners[tier_key]
        if not winners:
            if tier_key == "tier_5":
                rollover = prize_pool[pool_key]
            continue
        per = round(prize_pool[pool_key] / len(winners), 2)
        for u in winners:
            winner_docs.append({
                "id": str(uuid.uuid4()),
                "user_id": u["id"],
                "email": u["email"],
                "name": u["name"],
                "draw_id": draw["id"],
                "month": draw["month"],
                "tier": label,
                "prize_amount": per,
                "verification_status": "pending",  # pending|approved|rejected
                "payout_status": "pending",  # pending|paid
                "proof_storage_path": None,
                "created_at": now,
            })

    if winner_docs:
        await db.winners.insert_many(winner_docs)

    await db.draws.update_one(
        {"id": draw["id"]},
        {"$set": {
            "status": "published",
            "rollover_available": rollover,
            "published_at": now,
        }},
    )

    # Send emails (non-blocking-ish)
    for w in winner_docs:
        try:
            await send_email(w["email"], f"You won {w['tier']}!", render_winner(w["name"], w["tier"], w["prize_amount"]))
        except Exception:
            pass
    for u in users:
        try:
            await send_email(u["email"], f"{draw['month']} draw results", render_draw_result(u["name"], draw["month"], draw["numbers"]))
        except Exception:
            pass

    return {"published": True, "winners_count": len(winner_docs), "rollover": rollover}


@router.get("/latest")
async def latest_public():
    """Latest published draw — public."""
    from server import db
    draw = await db.draws.find_one({"status": "published"}, {"_id": 0}, sort=[("month", -1)])
    return draw or {}


@router.get("")
async def list_draws(limit: int = Query(12, ge=1, le=60)):
    from server import db
    items = await db.draws.find({"status": "published"}, {"_id": 0}).sort("month", -1).to_list(limit)
    return items


@router.get("/admin/all", dependencies=[Depends(admin_required)])
async def all_draws():
    from server import db
    return await db.draws.find({}, {"_id": 0}).sort("month", -1).to_list(100)


@router.get("/mine/participation")
async def my_participation(user: dict = Depends(get_current_user)):
    """User's match result per published draw."""
    from server import db
    draws = await db.draws.find({"status": "published"}, {"_id": 0}).sort("month", -1).to_list(12)
    last5_docs = await db.scores.find({"user_id": user["id"]}, {"_id": 0, "value": 1}).sort("date", -1).to_list(5)
    last5 = [s["value"] for s in last5_docs]
    out = []
    for d in draws:
        matches = count_matches(last5, d["numbers"]) if len(last5) == 5 else 0
        out.append({"month": d["month"], "numbers": d["numbers"], "matches": matches, "your_numbers": last5})
    return out
