-- =================================================================
-- Golf For Good — Supabase (Postgres) Schema
-- Run this ONCE in Supabase Dashboard → SQL Editor
-- =================================================================

-- Enable uuid generation
create extension if not exists "pgcrypto";

-- -----------------------------------------------------------------
-- users
-- -----------------------------------------------------------------
create table if not exists public.users (
  id                    text primary key,
  email                 text not null unique,
  password_hash         text not null,
  name                  text not null,
  role                  text not null default 'user',
  subscription_status   text not null default 'inactive',
  subscription_plan     text,
  subscription_end      timestamptz,
  charity_id            text,
  charity_percentage    numeric not null default 10,
  created_at            timestamptz not null default now()
);
create index if not exists idx_users_role on public.users(role);
create index if not exists idx_users_sub on public.users(subscription_status);

-- -----------------------------------------------------------------
-- charities
-- -----------------------------------------------------------------
create table if not exists public.charities (
  id                    text primary key,
  name                  text not null,
  short_description     text not null,
  description           text not null,
  image_url             text not null,
  category              text default 'General',
  events                jsonb not null default '[]'::jsonb,
  featured              boolean not null default false,
  created_at            timestamptz not null default now()
);
create index if not exists idx_charities_featured on public.charities(featured);

-- -----------------------------------------------------------------
-- scores   (Stableford 1-45, one per date per user, latest-5 rolling)
-- -----------------------------------------------------------------
create table if not exists public.scores (
  id                    text primary key,
  user_id               text not null,
  value                 integer not null check (value between 1 and 45),
  date                  text not null,
  created_at            timestamptz not null default now(),
  unique (user_id, date)
);
create index if not exists idx_scores_user on public.scores(user_id);
create index if not exists idx_scores_date on public.scores(date desc);

-- -----------------------------------------------------------------
-- payment_transactions
-- -----------------------------------------------------------------
create table if not exists public.payment_transactions (
  id                    text primary key,
  session_id            text not null unique,
  user_id               text not null,
  email                 text,
  amount                numeric not null,
  currency              text not null default 'usd',
  plan                  text,
  payment_status        text not null default 'initiated',
  metadata              jsonb default '{}'::jsonb,
  created_at            timestamptz not null default now(),
  completed_at          timestamptz
);
create index if not exists idx_payments_user on public.payment_transactions(user_id);
create index if not exists idx_payments_status on public.payment_transactions(payment_status);

-- -----------------------------------------------------------------
-- draws
-- -----------------------------------------------------------------
create table if not exists public.draws (
  id                    text primary key,
  month                 text not null unique,
  logic_type            text not null default 'random',
  numbers               integer[] not null default '{}',
  prize_pool            jsonb not null default '{}'::jsonb,
  active_users          integer not null default 0,
  status                text not null default 'draft',
  rollover_available    numeric not null default 0,
  created_at            timestamptz not null default now(),
  published_at          timestamptz
);
create index if not exists idx_draws_status on public.draws(status);

-- -----------------------------------------------------------------
-- winners
-- -----------------------------------------------------------------
create table if not exists public.winners (
  id                        text primary key,
  user_id                   text not null,
  email                     text not null,
  name                      text not null,
  draw_id                   text not null,
  month                     text not null,
  tier                      text not null,
  prize_amount              numeric not null,
  verification_status       text not null default 'pending',
  payout_status             text not null default 'pending',
  proof_storage_path        text,
  proof_uploaded_at         timestamptz,
  admin_note                text,
  created_at                timestamptz not null default now()
);
create index if not exists idx_winners_user on public.winners(user_id);
create index if not exists idx_winners_draw on public.winners(draw_id);

-- -----------------------------------------------------------------
-- files  (metadata for Emergent Object Storage uploads)
-- -----------------------------------------------------------------
create table if not exists public.files (
  id                    text primary key,
  user_id               text not null,
  storage_path          text not null unique,
  original_filename     text,
  content_type          text,
  size                  integer,
  is_deleted            boolean not null default false,
  created_at            timestamptz not null default now()
);
create index if not exists idx_files_user on public.files(user_id);

-- -----------------------------------------------------------------
-- RLS  — backend uses service_role key which bypasses RLS.
--         We disable RLS entirely because every write goes through
--         our FastAPI auth layer.  Re-enable & add policies later
--         if you expose Supabase directly to the browser.
-- -----------------------------------------------------------------
alter table public.users                 disable row level security;
alter table public.charities             disable row level security;
alter table public.scores                disable row level security;
alter table public.payment_transactions  disable row level security;
alter table public.draws                 disable row level security;
alter table public.winners               disable row level security;
alter table public.files                 disable row level security;
