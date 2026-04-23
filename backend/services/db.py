"""Supabase database helper.

We wrap the synchronous supabase-py client calls in asyncio.to_thread to
keep FastAPI non-blocking.  The tiny DB helper below also exposes a few
convenience methods that mirror what we previously used with Motor so
route code stays readable.
"""
import os
import asyncio
from typing import Any, Iterable
from supabase import create_client, Client


def _get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_KEY"]
    return create_client(url, key)


# Module-level singleton.
client: Client = _get_client()


async def run(fn):
    """Run a synchronous supabase call in a worker thread."""
    return await asyncio.to_thread(fn)


# ---------- High-level helpers -------------------------------------------------

async def select_one(table: str, filters: dict[str, Any] | None = None,
                     columns: str = "*") -> dict | None:
    def _op():
        q = client.table(table).select(columns)
        for k, v in (filters or {}).items():
            q = q.eq(k, v)
        return q.limit(1).execute()
    res = await run(_op)
    data = res.data or []
    return data[0] if data else None


async def select_many(table: str, filters: dict[str, Any] | None = None,
                      order_by: str | None = None, ascending: bool = True,
                      limit: int | None = None, columns: str = "*") -> list[dict]:
    def _op():
        q = client.table(table).select(columns)
        for k, v in (filters or {}).items():
            q = q.eq(k, v)
        if order_by:
            q = q.order(order_by, desc=not ascending)
        if limit:
            q = q.limit(limit)
        return q.execute()
    res = await run(_op)
    return res.data or []


async def insert_one(table: str, doc: dict) -> dict:
    def _op():
        return client.table(table).insert(doc).execute()
    res = await run(_op)
    return (res.data or [doc])[0]


async def insert_many(table: str, docs: list[dict]) -> list[dict]:
    if not docs:
        return []
    def _op():
        return client.table(table).insert(docs).execute()
    res = await run(_op)
    return res.data or []


async def update_by(table: str, filters: dict[str, Any], updates: dict) -> dict | None:
    def _op():
        q = client.table(table).update(updates)
        for k, v in filters.items():
            q = q.eq(k, v)
        return q.execute()
    res = await run(_op)
    data = res.data or []
    return data[0] if data else None


async def delete_by(table: str, filters: dict[str, Any]) -> int:
    def _op():
        q = client.table(table).delete()
        for k, v in filters.items():
            q = q.eq(k, v)
        return q.execute()
    res = await run(_op)
    return len(res.data or [])


async def count(table: str, filters: dict[str, Any] | None = None) -> int:
    def _op():
        q = client.table(table).select("id", count="exact")
        for k, v in (filters or {}).items():
            q = q.eq(k, v)
        return q.limit(1).execute()
    res = await run(_op)
    return res.count or 0


async def search_ilike(table: str, field: str, pattern: str,
                       extra_filters: dict[str, Any] | None = None,
                       columns: str = "*", limit: int = 500) -> list[dict]:
    def _op():
        q = client.table(table).select(columns).ilike(field, pattern)
        for k, v in (extra_filters or {}).items():
            q = q.eq(k, v)
        return q.limit(limit).execute()
    res = await run(_op)
    return res.data or []


async def select_by_in(table: str, field: str, values: Iterable[Any],
                       columns: str = "*") -> list[dict]:
    vals = list(values)
    if not vals:
        return []
    def _op():
        return client.table(table).select(columns).in_(field, vals).execute()
    res = await run(_op)
    return res.data or []


async def raw_rpc(name: str, params: dict | None = None) -> Any:
    def _op():
        return client.rpc(name, params or {}).execute()
    res = await run(_op)
    return res.data
