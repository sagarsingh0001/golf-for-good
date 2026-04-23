"""Draw and prize-pool routes."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query

from auth import admin_required, get_current_user
from models import DrawConfig, DrawPublishRequest
from services import db as sdb
from services.draw_engine import (
    random_numbers, algorithmic_numbers, count_matches, compute_prize_pool,
    MONTHLY_PRICE,
)
from services.email_service import send_email, render_winner, render_draw_result

router = APIRouter(prefix="/draws", tags=["draws"])


async def _build_draw(month: str, logic_type: str):
    if logic_type == "algorithmic":
        docs = await sdb.select_many("scores", columns="value", limit=10000)
        all_vals = [d["value"] for d in docs]
        nums = algorithmic_numbers(all_vals)
    else:
        nums = random_numbers()

    active_users = await sdb.count("users", {"subscription_status": "active"})
    subs_total = active_users * MONTHLY_PRICE

    # Latest published draw with unclaimed rollover
    prev_list = await sdb.select_many(
        "draws", {"status": "published"},
        order_by="month", ascending=False, limit=5,
    )
    rolled = 0.0
    for p in prev_list:
        rav = float(p.get("rollover_available") or 0)
        if rav > 0:
            rolled = rav
            break

    pool = compute_prize_pool(subs_total, rolled)
    return {"numbers": nums, "prize_pool": pool, "active_users": active_users}


@router.post("/configure", dependencies=[Depends(admin_required)])
async def configure(payload: DrawConfig):
    existing = await sdb.select_one("draws", {"month": payload.month})
    if existing and existing.get("status") == "published":
        raise HTTPException(400, "Draw for this month already published")

    built = await _build_draw(payload.month, payload.logic_type)
    doc = {
        "id": existing["id"] if existing else str(uuid.uuid4()),
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
        return await sdb.update_by("draws", {"month": payload.month}, doc)
    return await sdb.insert_one("draws", doc)


@router.post("/simulate", dependencies=[Depends(admin_required)])
async def simulate(payload: DrawConfig):
    built = await _build_draw(payload.month, payload.logic_type)
    users = await sdb.select_many("users", {"subscription_status": "active"}, columns="id", limit=10000)
    tier_counts = {"tier_5": 0, "tier_4": 0, "tier_3": 0}
    for u in users:
        last5 = await sdb.select_many(
            "scores", {"user_id": u["id"]}, columns="value",
            order_by="date", ascending=False, limit=5,
        )
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
    draw = await sdb.select_one("draws", {"id": payload.draw_id})
    if not draw:
        raise HTTPException(404, "Draw not found")
    if draw["status"] == "published":
        raise HTTPException(400, "Already published")

    users = await sdb.select_many(
        "users", {"subscription_status": "active", "role": "user"}, limit=10000,
    )
    tier_winners = {"tier_5": [], "tier_4": [], "tier_3": []}
    for u in users:
        last5 = await sdb.select_many(
            "scores", {"user_id": u["id"]}, columns="value,date",
            order_by="date", ascending=False, limit=5,
        )
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
                rollover = float(prize_pool.get(pool_key, 0) or 0)
            continue
        per = round(float(prize_pool.get(pool_key, 0) or 0) / len(winners), 2)
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
                "verification_status": "pending",
                "payout_status": "pending",
                "proof_storage_path": None,
                "created_at": now,
            })

    if winner_docs:
        await sdb.insert_many("winners", winner_docs)

    await sdb.update_by(
        "draws", {"id": draw["id"]},
        {"status": "published", "rollover_available": rollover, "published_at": now},
    )

    # Emails (best effort)
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
    items = await sdb.select_many("draws", {"status": "published"}, order_by="month", ascending=False, limit=1)
    return items[0] if items else {}


@router.get("")
async def list_draws(limit: int = Query(12, ge=1, le=60)):
    return await sdb.select_many("draws", {"status": "published"}, order_by="month", ascending=False, limit=limit)


@router.get("/admin/all", dependencies=[Depends(admin_required)])
async def all_draws():
    return await sdb.select_many("draws", order_by="month", ascending=False, limit=100)


@router.get("/mine/participation")
async def my_participation(user: dict = Depends(get_current_user)):
    draws = await sdb.select_many("draws", {"status": "published"}, order_by="month", ascending=False, limit=12)
    last5_docs = await sdb.select_many(
        "scores", {"user_id": user["id"]}, columns="value",
        order_by="date", ascending=False, limit=5,
    )
    last5 = [s["value"] for s in last5_docs]
    out = []
    for d in draws:
        matches = count_matches(last5, d["numbers"]) if len(last5) == 5 else 0
        out.append({"month": d["month"], "numbers": d["numbers"], "matches": matches, "your_numbers": last5})
    return out
