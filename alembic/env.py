"""Cấu hình Alembic.

Luật chống conflict migration nằm ở `api/README.md`: hai người cùng tạo
migration sẽ sinh hai revision cùng trỏ về một parent và làm gãy chain. Khi
conflict, **xoá migration của mình, pull, generate lại** — không bao giờ sửa
tay `down_revision`.
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Nạp model để autogenerate nhìn thấy đủ bảng. Thêm domain mới thì thêm một
# dòng import ở cuối khối này — chỉ thêm, không sắp xếp lại.
from api.battery import models as _battery  # noqa: F401
from api.catalog import models as _catalog  # noqa: F401
from api.core.db import Base, database_url
from api.orders import models as _orders  # noqa: F401
from api.pricing import models as _pricing  # noqa: F401
from api.promotions import models as _promotions  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", database_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
