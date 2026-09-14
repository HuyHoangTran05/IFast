"""Pin thuê là hợp đồng tài sản, có vòng đời riêng tách khỏi chiếc xe.

Ba bảng, ba lý do:

- `BatteryAsset` — pin là tài sản có định danh, cần biết nó hình thành khi nào,
  vì thời gian bảo hành áp dụng là chính sách **tại thời điểm hình thành**.
- `BatteryWarrantyPolicy` — chính sách bảo hành đổi theo thời gian, nên phải
  lưu được lịch sử chứ không phải một hằng số trong code.
- `BatteryListPrice` — giá pin công bố đổi theo thời gian, và công thức bồi
  thường tra giá **tại thời điểm xảy ra sự cố**, không phải giá hôm nay.
"""

from __future__ import annotations

import enum
from datetime import date

from sqlalchemy import BigInteger, Date, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.core.db import Base


class BatteryStatus(str, enum.Enum):
    LEASED = "leased"
    RETURNED = "returned"
    LOST = "lost"
    DAMAGED_BEYOND_REPAIR = "damaged_beyond_repair"


class BatteryAsset(Base):
    __tablename__ = "battery_asset"

    id: Mapped[int] = mapped_column(primary_key=True)
    serial: Mapped[str] = mapped_column(String(64), unique=True)
    trim_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[BatteryStatus] = mapped_column(Enum(BatteryStatus), default=BatteryStatus.LEASED)

    formed_on: Mapped[date] = mapped_column(Date)
    """Thời điểm hình thành tài sản. Mốc tra chính sách bảo hành."""


class BatteryWarrantyPolicy(Base):
    __tablename__ = "battery_warranty_policy"

    id: Mapped[int] = mapped_column(primary_key=True)
    warranty_months: Mapped[int] = mapped_column(Integer)

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class BatteryListPrice(Base):
    __tablename__ = "battery_list_price"

    id: Mapped[int] = mapped_column(primary_key=True)
    trim_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_vnd: Mapped[int] = mapped_column(BigInteger)

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
