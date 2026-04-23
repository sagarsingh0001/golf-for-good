"""Subscription and Stripe checkout routes."""
import os
import uuid
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest

from auth import get_current_user
from models import CheckoutRequest
from services import db as sdb
from services.draw_engine import MONTHLY_PRICE, YEARLY_PRICE

router = APIRouter(tags=["subscription"])
logger = logging.getLogger(__name__)

PLANS = {"monthly": MONTHLY_PRICE, "yearly": YEARLY_PRICE}


def _stripe_checkout(request: Request) -> StripeCheckout:
    api_key = os.environ["STRIPE_API_KEY"]
    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    return StripeCheckout(api_key=api_key, webhook_url=webhook_url)


@router.post("/subscribe/checkout")
async def create_checkout(payload: CheckoutRequest, request: Request, user: dict = Depends(get_current_user)):
    if payload.plan not in PLANS:
        raise HTTPException(400, "Invalid plan")

    amount = float(PLANS[payload.plan])
    origin = payload.origin_url.rstrip("/")
    success_url = f"{origin}/checkout/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin}/pricing"

    stripe = _stripe_checkout(request)
    session = await stripe.create_checkout_session(
        CheckoutSessionRequest(
            amount=amount,
            currency="usd",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"user_id": user["id"], "plan": payload.plan, "email": user["email"]},
        )
    )

    await sdb.insert_one("payment_transactions", {
        "id": str(uuid.uuid4()),
        "session_id": session.session_id,
        "user_id": user["id"],
        "email": user["email"],
        "amount": amount,
        "currency": "usd",
        "plan": payload.plan,
        "payment_status": "initiated",
        "metadata": {"plan": payload.plan},
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    return {"url": session.url, "session_id": session.session_id}


@router.get("/subscribe/status/{session_id}")
async def checkout_status(session_id: str, request: Request, user: dict = Depends(get_current_user)):
    tx = await sdb.select_one("payment_transactions", {"session_id": session_id})
    if not tx:
        raise HTTPException(404, "Transaction not found")

    try:
        stripe = _stripe_checkout(request)
        status = await stripe.get_checkout_status(session_id)
    except Exception as e:
        logger.warning(f"Stripe status lookup failed for {session_id}: {e}")
        return {
            "status": "unknown",
            "payment_status": tx.get("payment_status", "initiated"),
            "amount_total": int(float(tx.get("amount", 0)) * 100),
            "currency": tx.get("currency", "usd"),
        }

    if tx["payment_status"] != "paid" and status.payment_status == "paid":
        await sdb.update_by(
            "payment_transactions",
            {"session_id": session_id},
            {"payment_status": "paid", "completed_at": datetime.now(timezone.utc).isoformat()},
        )
        days = 365 if tx["plan"] == "yearly" else 31
        end = datetime.now(timezone.utc) + timedelta(days=days)
        await sdb.update_by(
            "users",
            {"id": tx["user_id"]},
            {"subscription_status": "active", "subscription_plan": tx["plan"], "subscription_end": end.isoformat()},
        )

    return {
        "status": status.status,
        "payment_status": status.payment_status,
        "amount_total": status.amount_total,
        "currency": status.currency,
    }


@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    try:
        stripe = _stripe_checkout(request)
        evt = await stripe.handle_webhook(body, signature)
    except Exception as e:
        logger.warning(f"Webhook handling failed: {e}")
        return {"received": False, "error": str(e)}

    if evt.payment_status == "paid" and evt.session_id:
        tx = await sdb.select_one("payment_transactions", {"session_id": evt.session_id})
        if tx and tx["payment_status"] != "paid":
            await sdb.update_by(
                "payment_transactions",
                {"session_id": evt.session_id},
                {"payment_status": "paid", "completed_at": datetime.now(timezone.utc).isoformat()},
            )
            days = 365 if tx["plan"] == "yearly" else 31
            end = datetime.now(timezone.utc) + timedelta(days=days)
            await sdb.update_by(
                "users",
                {"id": tx["user_id"]},
                {"subscription_status": "active", "subscription_plan": tx["plan"], "subscription_end": end.isoformat()},
            )
    return {"received": True}


@router.post("/subscribe/cancel")
async def cancel_subscription(user: dict = Depends(get_current_user)):
    await sdb.update_by("users", {"id": user["id"]}, {"subscription_status": "cancelled"})
    return {"ok": True}
