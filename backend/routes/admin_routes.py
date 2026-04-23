"""Admin routes — users + reports."""
from fastapi import APIRouter, Depends, HTTPException, Query
from auth import admin_required

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", dependencies=[Depends(admin_required)])
async def list_users(q: str | None = None, limit: int = Query(200, ge=1, le=1000)):
    from server import db
    filt = {}
    if q:
        filt = {"$or": [{"email": {"$regex": q, "$options": "i"}}, {"name": {"$regex": q, "$options": "i"}}]}
    items = await db.users.find(filt, {"_id": 0, "password_hash": 0}).to_list(limit)
    return items


@router.patch("/users/{user_id}", dependencies=[Depends(admin_required)])
async def update_user(user_id: str, payload: dict):
    from server import db
    allowed = {"name", "role", "subscription_status", "subscription_plan", "charity_id", "charity_percentage"}
    upd = {k: v for k, v in payload.items() if k in allowed}
    if not upd:
        raise HTTPException(400, "Nothing to update")
    res = await db.users.update_one({"id": user_id}, {"$set": upd})
    if res.matched_count == 0:
        raise HTTPException(404, "Not found")
    return await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})


@router.patch("/users/{user_id}/scores/{score_id}", dependencies=[Depends(admin_required)])
async def admin_edit_score(user_id: str, score_id: str, payload: dict):
    from server import db
    if "value" not in payload:
        raise HTTPException(400, "value required")
    res = await db.scores.update_one({"id": score_id, "user_id": user_id}, {"$set": {"value": int(payload["value"])}})
    if res.matched_count == 0:
        raise HTTPException(404, "Not found")
    return await db.scores.find_one({"id": score_id}, {"_id": 0})


@router.get("/users/{user_id}/scores", dependencies=[Depends(admin_required)])
async def admin_user_scores(user_id: str):
    from server import db
    return await db.scores.find({"user_id": user_id}, {"_id": 0}).sort("date", -1).to_list(50)


@router.get("/reports/summary", dependencies=[Depends(admin_required)])
async def reports_summary():
    from server import db
    total_users = await db.users.count_documents({"role": "user"})
    active_subs = await db.users.count_documents({"subscription_status": "active", "role": "user"})
    total_charities = await db.charities.count_documents({})
    total_winners = await db.winners.count_documents({})
    pending_payouts = await db.winners.count_documents({"payout_status": "pending"})
    latest_draw = await db.draws.find_one({"status": "published"}, {"_id": 0}, sort=[("month", -1)])
    prize_pool = latest_draw.get("prize_pool", {}).get("total_pool", 0.0) if latest_draw else 0.0

    # Payment totals
    paid = await db.payment_transactions.find({"payment_status": "paid"}, {"_id": 0, "amount": 1}).to_list(10000)
    total_revenue = sum(t["amount"] for t in paid)
    charity_contrib = 0.0
    for u in await db.users.find({"subscription_status": "active", "role": "user"}, {"_id": 0, "charity_percentage": 1, "subscription_plan": 1}).to_list(10000):
        plan = u.get("subscription_plan") or "monthly"
        est = 99.0 if plan == "yearly" else 9.99
        charity_contrib += est * (u.get("charity_percentage", 10.0) / 100.0)

    return {
        "total_users": total_users,
        "active_subscribers": active_subs,
        "total_charities": total_charities,
        "total_winners": total_winners,
        "pending_payouts": pending_payouts,
        "current_prize_pool": prize_pool,
        "total_revenue": round(total_revenue, 2),
        "charity_contribution_estimate": round(charity_contrib, 2),
    }
