"""Main FastAPI server for Golf For Good (Supabase-backed)."""
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

import os
import logging
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

from auth import hash_password, verify_password
from services import db as sdb

# --- App ---
app = FastAPI(title="Golf For Good API")
api_router = APIRouter(prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_origin_regex=r"https?://.*",
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@api_router.get("/")
async def root():
    return {"message": "Golf For Good API", "version": "1.0", "db": "supabase"}


@api_router.get("/health")
async def health():
    return {"status": "ok"}


# Register routes
from routes import (
    auth_routes, charity_routes, score_routes, subscription_routes,
    draw_routes, winner_routes, admin_routes, upload_routes,
    user_routes, public_routes,
)

api_router.include_router(auth_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(charity_routes.router)
api_router.include_router(score_routes.router)
api_router.include_router(subscription_routes.router)
api_router.include_router(draw_routes.router)
api_router.include_router(winner_routes.router)
api_router.include_router(upload_routes.router)
api_router.include_router(admin_routes.router)
api_router.include_router(public_routes.router)

app.include_router(api_router)


SAMPLE_CHARITIES = [
    {"name": "Clean Water Collective", "category": "Environment", "short_description": "Bringing clean water to communities in need.", "description": "Every dollar funds filtration systems in rural regions. Over 1.2M people served since 2014. Your contribution directly translates to drilled wells, maintained pumps, and trained local technicians.", "image_url": "https://images.unsplash.com/photo-1541544181051-e46607bc22a4?w=1200&q=80"},
    {"name": "Youth Mentor Network", "category": "Education", "short_description": "Connecting at-risk youth with lifelong mentors.", "description": "We pair under-served kids with volunteer professionals for long-term guidance. 87% of mentees graduate from high school — nearly double the regional average.", "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1200&q=80"},
    {"name": "Rewild Forests Initiative", "category": "Environment", "short_description": "Replanting native ecosystems, one acre at a time.", "description": "We work with indigenous communities and climate scientists to reforest critical habitats. Each subscription plants 4 trees per month.", "image_url": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=1200&q=80"},
    {"name": "Food Bridge", "category": "Hunger", "short_description": "Ending hunger in urban food deserts.", "description": "We partner with local grocers and farms to redirect surplus food to community pantries. 4.5 million meals served last year alone.", "image_url": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=1200&q=80"},
    {"name": "Open Hearts Animal Rescue", "category": "Animals", "short_description": "Rehabilitating and rehoming shelter animals.", "description": "A no-kill sanctuary providing medical care, socialization, and adoption services. Every dollar shelters 1 animal for a day.", "image_url": "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=1200&q=80"},
    {"name": "Veterans First", "category": "Community", "short_description": "Supporting veteran transition and mental health.", "description": "Counseling, housing assistance, and job placement for returning service members. Zero administrative overhead — every cent reaches a veteran.", "image_url": "https://images.unsplash.com/photo-1527474305487-b87b222841cc?w=1200&q=80"},
    {"name": "Ocean Restoration Project", "category": "Environment", "short_description": "Removing plastic from coastal ecosystems.", "description": "Fleet-based cleanup and community education in 14 coastal countries. 3.8 million pounds of plastic removed in 2024.", "image_url": "https://images.unsplash.com/photo-1583212292454-1fe6229603b7?w=1200&q=80"},
    {"name": "STEM for Her", "category": "Education", "short_description": "Putting girls on a path to tech careers.", "description": "Scholarships, labs, and mentorship for young women in STEM. 92% of alumnae pursue STEM degrees.", "image_url": "https://images.unsplash.com/photo-1573164713988-8665fc963095?w=1200&q=80"},
]


@app.on_event("startup")
async def startup():
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@golfforgood.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@1234")
    now_iso = datetime.now(timezone.utc).isoformat()

    # Seed admin
    try:
        existing = await sdb.select_one("users", {"email": admin_email})
        if not existing:
            await sdb.insert_one("users", {
                "id": str(uuid.uuid4()),
                "email": admin_email,
                "password_hash": hash_password(admin_password),
                "name": "Admin",
                "role": "admin",
                "subscription_status": "active",
                "subscription_plan": "admin",
                "subscription_end": None,
                "charity_id": None,
                "charity_percentage": 10.0,
                "created_at": now_iso,
            })
            logger.info("Admin seeded")
        elif not verify_password(admin_password, existing.get("password_hash", "")):
            await sdb.update_by("users", {"email": admin_email}, {"password_hash": hash_password(admin_password)})
            logger.info("Admin password refreshed")
    except Exception as e:
        logger.error(f"Seed admin failed (did you run supabase_schema.sql?): {e}")
        return

    # Seed test subscriber
    test_email = "test@golfforgood.com"
    test_existing = await sdb.select_one("users", {"email": test_email})
    if not test_existing:
        now = datetime.now(timezone.utc)
        nxt_month = now.replace(year=now.year + (1 if now.month == 12 else 0), month=(now.month % 12) + 1)
        await sdb.insert_one("users", {
            "id": str(uuid.uuid4()),
            "email": test_email,
            "password_hash": hash_password("Test@1234"),
            "name": "Alex Test",
            "role": "user",
            "subscription_status": "active",
            "subscription_plan": "monthly",
            "subscription_end": nxt_month.isoformat(),
            "charity_id": None,
            "charity_percentage": 10.0,
            "created_at": now_iso,
        })

    # Seed charities if empty
    if await sdb.count("charities") == 0:
        docs = []
        for i, c in enumerate(SAMPLE_CHARITIES):
            docs.append({
                "id": str(uuid.uuid4()),
                **c,
                "events": [],
                "featured": i == 0,
                "created_at": now_iso,
            })
        await sdb.insert_many("charities", docs)
        logger.info("Charities seeded")

    # Link test user to first charity
    first = await sdb.select_one("charities")
    if first:
        tu = await sdb.select_one("users", {"email": test_email})
        if tu and not tu.get("charity_id"):
            await sdb.update_by("users", {"email": test_email}, {"charity_id": first["id"]})

    # Credentials file
    Path("/app/memory").mkdir(parents=True, exist_ok=True)
    Path("/app/memory/test_credentials.md").write_text(
        f"""# Test Credentials

## Admin
- Email: {admin_email}
- Password: {admin_password}
- Role: admin

## Test Subscriber
- Email: test@golfforgood.com
- Password: Test@1234
- Role: user

## Auth Endpoints
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET  /api/auth/me
"""
    )
    logger.info("Startup complete (Supabase)")
