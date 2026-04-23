"""Auth routes."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from models import UserRegister, UserLogin
from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, get_current_user,
)
from services.email_service import send_email, render_welcome

router = APIRouter(prefix="/auth", tags=["auth"])


def _public_user(u: dict) -> dict:
    u = {k: v for k, v in u.items() if k not in ("password_hash", "_id")}
    return u


@router.post("/register")
async def register(payload: UserRegister, response: Response):
    from server import db
    email = payload.email.lower().strip()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate charity if provided
    charity_id = payload.charity_id
    if charity_id:
        c = await db.charities.find_one({"id": charity_id})
        if not c:
            raise HTTPException(status_code=400, detail="Invalid charity")

    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(payload.password),
        "name": payload.name,
        "role": "user",
        "subscription_status": "inactive",
        "subscription_plan": None,
        "subscription_end": None,
        "charity_id": charity_id,
        "charity_percentage": max(10.0, payload.charity_percentage or 10.0),
        "created_at": now,
    }
    await db.users.insert_one(doc)

    access = create_access_token(user_id, email, "user")
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)

    # Fire-and-forget welcome email
    try:
        await send_email(email, "Welcome to Golf For Good", render_welcome(payload.name))
    except Exception:
        pass

    return _public_user(doc)


@router.post("/login")
async def login(payload: UserLogin, response: Response):
    from server import db
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access = create_access_token(user["id"], user["email"], user.get("role", "user"))
    refresh = create_refresh_token(user["id"])
    set_auth_cookies(response, access, refresh)
    return _public_user(user)


@router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"ok": True}


@router.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user
