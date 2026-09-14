"""Phiên CSDL và lớp Base dùng chung.

PostgreSQL khi chạy thật, SQLite khi chạy test — test không được phụ thuộc
Docker, nếu không sẽ không ai chạy test.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def database_url() -> str:
    return os.environ.get("IFAST_DATABASE_URL", "sqlite+pysqlite:///./ifast.db")


_engine = None
_SessionLocal = None


def engine():
    global _engine
    if _engine is None:
        url = database_url()
        kwargs = {"future": True}
        if url.startswith("sqlite"):
            kwargs["connect_args"] = {"check_same_thread": False}
        _engine = create_engine(url, **kwargs)
    return _engine


def session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=engine(), autoflush=False, future=True)
    return _SessionLocal


def get_session() -> Iterator[Session]:
    with session_factory()() as session:
        yield session
