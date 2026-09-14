#!/usr/bin/env python
"""Tạo bảng và nạp dữ liệu mẫu vào CSDL phát triển.

    python scripts/seed-dev.py

Dùng SQLite mặc định. Đặt IFAST_DATABASE_URL để trỏ sang PostgreSQL.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

from sqlalchemy.orm import Session  # noqa: E402

from api.battery import models as _battery  # noqa: F401,E402
from api.catalog import models as _catalog  # noqa: F401,E402
from api.core.db import Base, database_url, engine  # noqa: E402
from api.orders import models as _orders  # noqa: F401,E402
from api.pricing import models as _pricing  # noqa: F401,E402
from api.promotions import models as _promotions  # noqa: F401,E402
from api.seed import seed  # noqa: E402


def main() -> int:
    Base.metadata.create_all(engine())
    with Session(engine()) as session:
        seed(session)
    print(f"đã nạp dữ liệu mẫu vào {database_url()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
