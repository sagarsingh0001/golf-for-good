# ============================================================
# Golf For Good — Environment Variables Reference
# ============================================================
# This file consolidates every env var used across the app.
# For deployment: copy the relevant block to your host's env
# settings (Emergent / Vercel / Railway / Render etc.).
#
# ⚠️  This file contains SECRETS. Do NOT commit it to a public
#     repo. Add it to .gitignore.
# ============================================================


# ------------------------------------------------------------
# BACKEND  (FastAPI — /app/backend/.env)
# ------------------------------------------------------------

# --- MongoDB ---
MONGO_URL="mongodb://localhost:27017"
DB_NAME="test_database"

# --- CORS ---
CORS_ORIGINS="*"

# --- Auth (JWT) ---
JWT_SECRET="a7f3e9b1c2d4e6f8a0b1c3d5e7f9a2b4c6d8e0f1a3b5c7d9e1f3a5b7c9d1e3f5"
ADMIN_EMAIL="admin@golfforgood.com"
ADMIN_PASSWORD="Admin@1234"

# --- Stripe (test key provided by Emergent) ---
STRIPE_API_KEY="sk_test_emergent"

# --- Resend (transactional email) ---
RESEND_API_KEY="re_C9jPUEwn_HQBeAZBwCsZtHqSUhgFJFTrc"
SENDER_EMAIL="onboarding@resend.dev"
NOTIFICATION_DEST_EMAIL="sagarsinghtransformers@gmail.com"

# --- Emergent Object Storage (winner proof uploads) ---
EMERGENT_LLM_KEY="sk-emergent-4E07132BbF4A0894eE"
APP_NAME="golfforgood"


# ------------------------------------------------------------
# FRONTEND  (React — /app/frontend/.env)
# ------------------------------------------------------------

REACT_APP_BACKEND_URL=https://design-to-web-62.preview.emergentagent.com
WDS_SOCKET_PORT=443
ENABLE_HEALTH_CHECK=false


# ============================================================
# Notes for Production Deployment
# ============================================================
#
# 1. MONGO_URL / DB_NAME
#    - Replace with a MongoDB Atlas URI when deploying outside Emergent.
#      e.g. mongodb+srv://<user>:<pass>@cluster.mongodb.net/golfforgood
#
# 2. CORS_ORIGINS
#    - For production, change "*" to an explicit comma-separated list:
#      CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
#
# 3. JWT_SECRET
#    - Rotate to a new random 64-char hex value before going live.
#      Generate: python -c "import secrets; print(secrets.token_hex(32))"
#
# 4. ADMIN_EMAIL / ADMIN_PASSWORD
#    - Change defaults before your first production boot;
#      the server auto-reseeds on startup if password differs.
#
# 5. STRIPE_API_KEY
#    - Replace sk_test_emergent with your real Stripe secret key
#      (sk_live_... for production).  Configure Stripe webhook
#      endpoint: {YOUR_BACKEND_URL}/api/webhook/stripe
#
# 6. RESEND_API_KEY / SENDER_EMAIL
#    - Verify a custom sending domain in Resend for production,
#      then change SENDER_EMAIL to e.g. noreply@yourdomain.com.
#
# 7. EMERGENT_LLM_KEY
#    - Provided by Emergent platform.  When deploying outside
#      Emergent, you must implement object storage with your own
#      provider (S3, R2, GCS, etc.) or keep this key and continue
#      using Emergent Object Storage.
#
# 8. REACT_APP_BACKEND_URL
#    - Must point to the PUBLIC URL of your deployed backend
#      (e.g. https://api.yourdomain.com).  Must be set at build
#      time — CRA inlines it into the bundle.
#
# ============================================================
