# Golf For Good — PRD & Build Log

## Original Problem Statement
> Go through this PRD and make website sticking to the instructions.

PRD: `Product Requirements Document` from Digital Heroes — a subscription-driven web app combining golf performance tracking (Stableford), monthly draw-based prize engine, and charity fundraising.

## User Choices (verbatim)
- Auth: JWT custom (email/password)
- Payments: real Stripe (test key `sk_test_emergent`)
- Emails: Resend (`re_C9jPUEwn_*`, `sagarsinghtransformers@gmail.com`)
- Uploads: Emergent Object Storage
- Design: design_agent decides (editorial, Charity-Water / Kickstarter aesthetic)

## Architecture
- **Backend**: FastAPI, modular `routes/*`, `services/*`, MongoDB (motor), JWT (bcrypt), `emergentintegrations` for Stripe, `resend` for email.
- **Frontend**: React 19 + React Router 7, Tailwind + shadcn/ui, framer-motion, react-fast-marquee, Outfit + Work Sans fonts. Off-white `#F9F8F6` bg, forest-green `#1E3A2F` primary, terracotta `#D95D39` accent.
- **DB collections**: users, scores, charities, subscriptions (logical via users), payment_transactions, draws, winners, files, login_attempts.

## Personas
1. **Public visitor** — browses charities, learns, subscribes.
2. **Subscriber** — manages scores, picks charity, participates in monthly draws, uploads winner proof.
3. **Admin** — configures/simulates/publishes draws, manages users, CRUD charities, verifies winners, marks payouts, views reports.

## Implemented (Feb 2026)
- [x] JWT auth: register/login/logout/me with httpOnly cookies
- [x] Seed: admin `admin@golfforgood.com` / `Admin@1234`, test user `test@golfforgood.com` / `Test@1234`, 8 charities
- [x] Charities public listing + filter/search + detail + admin CRUD
- [x] Score entry: Stableford 1–45, 1/date, last-5 rolling eviction
- [x] Stripe checkout (monthly $9.99, yearly $99) with `/api/webhook/stripe` + `/api/subscribe/status/{sid}` polling + server-defined amounts; `/api/subscribe/cancel`
- [x] Draw engine: random + algorithmic (score-weighted), configure/simulate/publish, 5/4/3 tier splits (40/35/25%), jackpot rollover when no 5-match
- [x] Winner verification: upload screenshot (≤5MB images) to Emergent Object Storage; admin approve/reject; payout pending → paid
- [x] Resend emails: welcome, draw results, winner alert (non-blocking)
- [x] Admin panel: overview/reports, users, charities, draws, winners
- [x] RBAC: non-admins blocked from `/admin/*` routes (frontend + backend)
- [x] Dashboard: subscription, charity, participation cards + recent scores + winnings
- [x] Responsive, mobile-first; hero/marquee/grid/CTA all working
- [x] 33/35 backend tests passing (2 skipped — upload happy-path needs a seeded winner); 100% of frontend flows pass

## Known Deferred / P1
- Login brute-force lockout (playbook recommendation).
- Move emails into `BackgroundTasks` to avoid request latency.
- Prize-pool estimate: currently multiplies active_users × MONTHLY_PRICE; should sum actual plan amounts.
- Strict CORS pin (currently `*` + regex fallback).
- Scalability: campaign module placeholder, team/corporate accounts, i18n for multi-country.

## P2 / Nice-to-have
- Stripe webhook signature verification tightening
- Email preferences + unsubscribe page
- Score import (CSV)
- Public leaderboard / community stats
