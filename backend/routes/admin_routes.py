"""Admin routes — users + reports."""
from fastapi import APIRouter, Depends, HTTPException, Query
from auth import admin_required
from services import db as sdb

router = APIRouter(prefix="/admin", tags=["admin"])

ALLOWED_USER_FIELDS = {"name", "role", "subscription_status", "subscription_plan", "charity_id", "charity_percentage"}


def _strip(u: dict) -> dict:
    return {k: v for k, v in u.items() if k != "password_hash"}


@router.get("/users", dependencies=[Depends(admin_required)])
async def list_users(q: str | None = None, limit: int = Query(200, ge=1, le=1000)):
    if q:
        # Use OR via PostgREST by doing two ilike queries and merging
        by_email = await sdb.search_ilike("users", "email", f"%{q}%", limit=limit)
        by_name = await sdb.search_ilike("users", "name", f"%{q}%", limit=limit)
        seen, out = set(), []
        for u in (by_email + by_name):
            if u["id"] not in seen:
                seen.add(u["id"])
                out.append(_strip(u))
        return out
    items = await sdb.select_many("users", order_by="created_at", ascending=False, limit=limit)
    return [_strip(u) for u in items]


@router.patch("/users/{user_id}", dependencies=[Depends(admin_required)])
async def update_user(user_id: str, payload: dict):
    upd = {k: v for k, v in payload.items() if k in ALLOWED_USER_FIELDS}
    if not upd:
        raise HTTPException(400, "Nothing to update")
    updated = await sdb.update_by("users", {"id": user_id}, upd)
    if not updated:
        raise HTTPException(404, "Not found")
    return _strip(updated)


@router.patch("/users/{user_id}/scores/{score_id}", dependencies=[Depends(admin_required)])
async def admin_edit_score(user_id: str, score_id: str, payload: dict):
    if "value" not in payload:
        raise HTTPException(400, "value required")
    existing = await sdb.select_one("scores", {"id": score_id, "user_id": user_id})
    if not existing:
        raise HTTPException(404, "Not found")
    return await sdb.update_by("scores", {"id": score_id}, {"value": int(payload["value"])})


@router.get("/users/{user_id}/scores", dependencies=[Depends(admin_required)])
async def admin_user_scores(user_id: str):
    return await sdb.select_many(
        "scores", {"user_id": user_id},
        order_by="date", ascending=False, limit=50,
    )


@router.get("/reports/summary", dependencies=[Depends(admin_required)])
async def reports_summary():
    total_users = await sdb.count("users", {"role": "user"})
    active_subs = await sdb.count("users", {"subscription_status": "active", "role": "user"})
    total_charities = await sdb.count("charities")
    total_winners = await sdb.count("winners")
    pending_payouts = await sdb.count("winners", {"payout_status": "pending"})

    latest_list = await sdb.select_many(
        "draws", {"status": "published"},
        order_by="month", ascending=False, limit=1,
    )
    prize_pool = 0.0
    if latest_list:
        pp = latest_list[0].get("prize_pool") or {}
        prize_pool = float(pp.get("total_pool", 0.0))

    paid = await sdb.select_many(
        "payment_transactions", {"payment_status": "paid"},
        columns="amount", limit=10000,
    )
    total_revenue = sum(float(t["amount"]) for t in paid)

    active_for_charity = await sdb.select_many(
        "users", {"subscription_status": "active", "role": "user"},
        columns="charity_percentage,subscription_plan", limit=10000,
    )
    charity_contrib = 0.0
    for u in active_for_charity:
        plan = u.get("subscription_plan") or "monthly"
        est = 99.0 if plan == "yearly" else 9.99
        charity_contrib += est * (float(u.get("charity_percentage", 10.0)) / 100.0)

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
