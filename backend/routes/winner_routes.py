"""Winner verification & payout routes."""
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user, admin_required
from models import WinnerVerify, WinnerPayoutUpdate
from services import db as sdb

router = APIRouter(prefix="/winners", tags=["winners"])


@router.get("/mine")
async def my_winnings(user: dict = Depends(get_current_user)):
    return await sdb.select_many(
        "winners", {"user_id": user["id"]},
        order_by="created_at", ascending=False, limit=100,
    )


@router.get("/admin/all", dependencies=[Depends(admin_required)])
async def admin_list():
    return await sdb.select_many("winners", order_by="created_at", ascending=False, limit=500)


@router.post("/verify", dependencies=[Depends(admin_required)])
async def verify(payload: WinnerVerify):
    status = "approved" if payload.action == "approve" else "rejected"
    updated = await sdb.update_by(
        "winners", {"id": payload.winner_id},
        {"verification_status": status, "admin_note": payload.note},
    )
    if not updated:
        raise HTTPException(404, "Winner not found")
    return {"ok": True, "status": status}


@router.post("/payout", dependencies=[Depends(admin_required)])
async def payout(payload: WinnerPayoutUpdate):
    updated = await sdb.update_by(
        "winners", {"id": payload.winner_id},
        {"payout_status": payload.payout_status},
    )
    if not updated:
        raise HTTPException(404, "Winner not found")
    return {"ok": True}
