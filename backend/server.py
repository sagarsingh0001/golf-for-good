"""Main FastAPI server for Golf For Good."""
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
from motor.motor_asyncio import AsyncIOMotorClient

from auth import hash_password, verify_password

# --- MongoDB ---
mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

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

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@api_router.get("/")
async def root():
    return {"message": "Golf For Good API", "version": "1.0"}


@api_router.get("/health")
async def health():
    return {"status": "ok"}


# Import & register routes
from routes import auth_routes, charity_routes, score_routes, subscription_routes
from routes import draw_routes, winner_routes, admin_routes, upload_routes, user_routes, public_routes

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


# --- Seeding ---
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
    # Indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.scores.create_index([("user_id", 1), ("date", 1)], unique=True)
    await db.charities.create_index("id", unique=True)
    await db.draws.create_index([("month", 1)], unique=True)
    await db.winners.create_index("id", unique=True)

    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@golfforgood.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@1234")
    existing = await db.users.find_one({"email": admin_email})
    now_iso = datetime.now(timezone.utc).isoformat()
    if not existing:
        await db.users.insert_one({
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
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
        logger.info("Admin password updated")

    # Seed test user (subscriber)
    test_email = "test@golfforgood.com"
    test_existing = await db.users.find_one({"email": test_email})
    if not test_existing:
        # Pick first charity below if exists later
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": test_email,
            "password_hash": hash_password("Test@1234"),
            "name": "Alex Test",
            "role": "user",
            "subscription_status": "active",
            "subscription_plan": "monthly",
            "subscription_end": (datetime.now(timezone.utc).replace(month=(datetime.now(timezone.utc).month % 12) + 1)).isoformat() if datetime.now(timezone.utc).month < 12 else datetime.now(timezone.utc).replace(year=datetime.now(timezone.utc).year + 1, month=1).isoformat(),
            "charity_id": None,
            "charity_percentage": 10.0,
            "created_at": now_iso,
        })

    # Seed charities
    if await db.charities.count_documents({}) == 0:
        for i, c in enumerate(SAMPLE_CHARITIES):
            doc = {
                "id": str(uuid.uuid4()),
                **c,
                "events": [],
                "featured": i == 0,
                "created_at": now_iso,
            }
            await db.charities.insert_one(doc)
        logger.info("Charities seeded")

    # Link test user to first charity
    first_charity = await db.charities.find_one({}, {"_id": 0, "id": 1})
    if first_charity:
        await db.users.update_one(
            {"email": test_email, "charity_id": None},
            {"$set": {"charity_id": first_charity["id"]}},
        )

    # Write test credentials
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

    logger.info("Startup complete")


@app.on_event("shutdown")
async def shutdown():
    client.close()
