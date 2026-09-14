"""Test chạy trên SQLite trong bộ nhớ.

Test không được phụ thuộc Docker hay PostgreSQL: test nào cần dựng hạ tầng mới
chạy được thì sẽ không ai chạy, và không ai chạy thì test vô dụng.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.core.db import Base, get_session
from api.main import app
from api.seed import seed

# Nạp toàn bộ model để Base.metadata biết hết bảng trước khi create_all.
from api.battery import models as _battery  # noqa: F401,E402
from api.catalog import models as _catalog  # noqa: F401,E402
from api.orders import models as _orders  # noqa: F401,E402
from api.pricing import models as _pricing  # noqa: F401,E402
from api.promotions import models as _promotions  # noqa: F401,E402


@pytest.fixture()
def session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, future=True)
    with factory() as s:
        seed(s)
        yield s
    Base.metadata.drop_all(engine)


@pytest.fixture()
def client(session: Session) -> TestClient:
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
