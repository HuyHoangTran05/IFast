"""Đơn hàng và bất biến snapshot.

Khi khách chốt đơn, toàn bộ giá, ưu đãi và cấu hình xe được **chụp lại vào
chính đơn hàng**. Sau đó đơn không đọc lại bảng giá nữa.

Hai lý do, và cả hai đều quan trọng:

- Nghiệp vụ: bảng giá đổi ngày mai không được làm đổi đơn ký hôm nay. Khách đã
  ký hợp đồng với một con số cụ thể.
- Tổ chức: đơn không phụ thuộc runtime vào `pricing/`, nên R2b sửa đơn hàng mà
  không phải chờ R2a, và ngược lại.
"""

from __future__ import annotations

import enum
from datetime import UTC, date, datetime

from sqlalchemy import JSON, BigInteger, Date, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from api.core.db import Base


class OrderChannel(enum.StrEnum):
    """Hai luồng mua khác nhau, không ép chung một máy trạng thái.

    Ô tô đi qua đặt cọc rồi hợp đồng rồi giao xe. Xe máy và phụ kiện mua thẳng.
    """

    DEPOSIT = "deposit"
    DIRECT_PURCHASE = "direct_purchase"


class OrderStatus(enum.StrEnum):
    DRAFT = "draft"
    DEPOSIT_PENDING = "deposit_pending"
    DEPOSIT_PAID = "deposit_paid"
    CONTRACT_SIGNED = "contract_signed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders_order"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    customer_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    channel: Mapped[OrderChannel] = mapped_column(Enum(OrderChannel))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.DRAFT)

    trim_id: Mapped[int] = mapped_column(Integer)
    province_code: Mapped[str] = mapped_column(String(16))

    quoted_on: Mapped[date] = mapped_column(Date)
    """Mốc thời gian đã dùng để tính mọi con số trong snapshot."""

    price_snapshot: Mapped[dict] = mapped_column(JSON)
    """Ảnh chụp bất biến: giá, ưu đãi đã áp, phần tách khoản lăn bánh.

    Không bao giờ ghi đè sau khi đơn rời trạng thái DRAFT.
    """

    total_vnd: Mapped[int] = mapped_column(BigInteger)
    deposit_vnd: Mapped[int] = mapped_column(BigInteger, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
