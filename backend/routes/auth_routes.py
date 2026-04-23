"""Auth routes."""
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Response, Depends

from models import UserRegister, UserLogin
from auth import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    set_auth_cookies, clear_auth_cookies, get_current_user,
)
from services import db as sdb
from services.email_service import send_email, render_welcome

router = APIRouter(prefix="/auth", tags=["auth"])


def _public_user(u: dict) -> dict:
    return {k: v for k, v in u.items() if k != "password_hash"}


@router.post("/register")
async def register(payload: UserRegister, response: Response):
    email = payload.email.lower().strip()
    if await sdb.select_one("users", {"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    if payload.charity_id:
        if not await sdb.select_one("charities", {"id": payload.charity_id}):
            raise HTTPException(status_code=400, detail="Invalid charity")

    user_id = str(uuid.uuid4())
    doc = {
        "id": user_id,
        "email": email,
        "password_hash": hash_password(payload.password),
        "name": payload.name,
        "role": "user",
        "subscription_status": "inactive",
        "subscription_plan": None,
        "subscription_end": None,
        "charity_id": payload.charity_id,
        "charity_percentage": float(max(10.0, payload.charity_percentage or 10.0)),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    created = await sdb.insert_one("users", doc)

    access = create_access_token(user_id, email, "user")
    refresh = create_refresh_token(user_id)
    set_auth_cookies(response, access, refresh)

    try:
        await send_email(email, "Welcome to Golf For Good", render_welcome(payload.name))
    except Exception:
        pass

    return _public_user(created)


@router.post("/login")
async def login(payload: UserLogin, response: Response):
    email = payload.email.lower().strip()
    user = await sdb.select_one("users", {"email": email})
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
