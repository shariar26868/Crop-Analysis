import asyncio
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException
from app.config import DATABASE_URL
from typing import Iterable

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

def _run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    normalized = sql.strip().lower()
    if not normalized.startswith(("select", "with")):
        raise ValueError("run_query only supports read-only SELECT/WITH queries.")

    try:
        if params:
            return pd.read_sql(text(sql), engine, params=params)

        return pd.read_sql(text(sql), engine)
    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Please try again later."
        ) from exc


async def run_query(sql: str, params: dict | None = None) -> pd.DataFrame:
    return await asyncio.to_thread(_run_query, sql, params)

def _run_write(sql: str, params: dict | None = None):
    normalized = sql.strip().lower()
    if normalized.startswith(("select", "with")):
        raise ValueError("run_write does not support SELECT queries.")

    try:
        with engine.begin() as conn:
            if params:
                conn.execute(text(sql), params)
            else:
                conn.execute(text(sql))
    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Please try again later."
        ) from exc

async def run_write(sql: str, params: dict | None = None, invalidate_prefixes: Iterable[str] | None = None):
    """Run a write (INSERT/UPDATE/DELETE) in a thread, then invalidate cache prefixes.

    Callers should `await run_write(...)` from async endpoints. Pass `invalidate_prefixes`
    to remove cache keys matching those prefixes after the DB write completes.
    """
    await asyncio.to_thread(_run_write, sql, params)

    if invalidate_prefixes:
        from app.cache import invalidate_prefix
        for p in invalidate_prefixes:
            try:
                await invalidate_prefix(p)
            except Exception:
                pass
