"""Public stats — safe aggregate numbers for marketing pages."""
from fastapi import APIRouter

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/stats")
async def public_stats():
    from server import db
    active_subs = await db.users.count_documents({"subscription_status": "active", "role": "user"})
    total_users = await db.users.count_documents({"role": "user"})
    total_charities = await db.charities.count_documents({})

    # Total charitable contribution (estimate from active subs × plan price × their percentage)
    charity_contrib = 0.0
    async for u in db.users.find({"subscription_status": "active", "role": "user"}, {"_id": 0, "charity_percentage": 1, "subscription_plan": 1}):
        plan = u.get("subscription_plan") or "monthly"
        est = 99.0 if plan == "yearly" else 9.99
        charity_contrib += est * (u.get("charity_percentage", 10.0) / 100.0)

    # Total prizes awarded (paid winners)
    paid_winners = await db.winners.find({"payout_status": "paid"}, {"_id": 0, "prize_amount": 1}).to_list(10000)
    total_prizes_paid = sum(w.get("prize_amount", 0) for w in paid_winners)

    total_winners = await db.winners.count_documents({})

    # Current prize pool (latest published draw)
    latest = await db.draws.find_one({"status": "published"}, {"_id": 0}, sort=[("month", -1)])
    current_pool = latest.get("prize_pool", {}).get("total_pool", 0.0) if latest else 0.0

    return {
        "active_subscribers": active_subs,
        "total_users": total_users,
        "total_charities": total_charities,
        "charity_contribution_total": round(charity_contrib, 2),
        "total_prizes_paid": round(total_prizes_paid, 2),
        "total_winners": total_winners,
        "current_prize_pool": current_pool,
    }
