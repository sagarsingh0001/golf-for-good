"""Public stats — safe aggregate numbers for marketing pages."""
from fastapi import APIRouter
from services import db as sdb

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/stats")
async def public_stats():
    active_subs = await sdb.count("users", {"subscription_status": "active", "role": "user"})
    total_users = await sdb.count("users", {"role": "user"})
    total_charities = await sdb.count("charities")

    actives = await sdb.select_many(
        "users", {"subscription_status": "active", "role": "user"},
        columns="charity_percentage,subscription_plan", limit=10000,
    )
    charity_contrib = 0.0
    for u in actives:
        plan = u.get("subscription_plan") or "monthly"
        est = 99.0 if plan == "yearly" else 9.99
        charity_contrib += est * (float(u.get("charity_percentage", 10.0)) / 100.0)

    paid_winners = await sdb.select_many(
        "winners", {"payout_status": "paid"},
        columns="prize_amount", limit=10000,
    )
    total_prizes_paid = sum(float(w.get("prize_amount", 0) or 0) for w in paid_winners)

    total_winners = await sdb.count("winners")

    latest_list = await sdb.select_many(
        "draws", {"status": "published"},
        order_by="month", ascending=False, limit=1,
    )
    current_pool = 0.0
    if latest_list:
        pp = latest_list[0].get("prize_pool") or {}
        current_pool = float(pp.get("total_pool", 0.0))

    return {
        "active_subscribers": active_subs,
        "total_users": total_users,
        "total_charities": total_charities,
        "charity_contribution_total": round(charity_contrib, 2),
        "total_prizes_paid": round(total_prizes_paid, 2),
        "total_winners": total_winners,
        "current_prize_pool": current_pool,
    }
