"""Winner verification & payout routes."""
from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user, admin_required
from models import WinnerVerify, WinnerPayoutUpdate

router = APIRouter(prefix="/winners", tags=["winners"])


@router.get("/mine")
async def my_winnings(user: dict = Depends(get_current_user)):
    from server import db
    items = await db.winners.find({"user_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(100)
    return items


@router.get("/admin/all", dependencies=[Depends(admin_required)])
async def admin_list():
    from server import db
    return await db.winners.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)


@router.post("/verify", dependencies=[Depends(admin_required)])
async def verify(payload: WinnerVerify):
    from server import db
    status = "approved" if payload.action == "approve" else "rejected"
    res = await db.winners.update_one(
        {"id": payload.winner_id},
        {"$set": {"verification_status": status, "admin_note": payload.note}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "Winner not found")
    return {"ok": True, "status": status}


@router.post("/payout", dependencies=[Depends(admin_required)])
async def payout(payload: WinnerPayoutUpdate):
    from server import db
    res = await db.winners.update_one(
        {"id": payload.winner_id},
        {"$set": {"payout_status": payload.payout_status}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "Winner not found")
    return {"ok": True}
