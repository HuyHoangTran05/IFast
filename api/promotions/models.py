"""Ưu đãi là thực thể có vòng đời, không phải một cột giảm giá.

Trang thật có ưu đãi dạng "miễn phí sạc từ ngày 10/02/2026" — tức là ưu đãi có
mốc bắt đầu, có điều kiện áp dụng, và có thể tồn tại nhiều ưu đãi cùng lúc.
Một cột `discount` trên bảng giá không diễn đạt được bất kỳ điều nào trong đó.
"""

from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, Enum, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from api.core.db import Base


class PromotionKind(enum.StrEnum):
    FIXED_AMOUNT = "fixed_amount"
    PERCENT_OF_PRICE = "percent_of_price"
    BENEFIT_IN_KIND = "benefit_in_kind"


class Promotion(Base):
    __tablename__ = "promotions_promotion"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    terms_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    kind: Mapped[PromotionKind] = mapped_column(Enum(PromotionKind))
    amount_vnd: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    percent: Mapped[Decimal | None] = mapped_column(Numeric(6, 4), nullable=True)

    trim_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    province_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    ownership_model: Mapped[str | None] = mapped_column(String(32), nullable=True)

    priority: Mapped[int] = mapped_column(Integer, default=0)
    stackable: Mapped[bool] = mapped_column(Boolean, default=False)

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
