"""Bảng giá và bảng phí, tất cả đều có ngày hiệu lực.

Không có bảng nào ở đây được phép chỉ mang "giá hiện tại". Trang VinFast thật
hiển thị giá niêm yết bên cạnh giá ưu đãi, giá nhiên liệu tham chiếu có ngày
cập nhật, và chính sách miễn phí sạc có ngày bắt đầu — nghĩa là mọi con số đều
là một hàm của thời gian.
"""

from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from api.core.db import Base


class OwnershipModel(enum.StrEnum):
    """Hai mô hình sở hữu pin. Đây là hai biến thể giá, không phải một cờ."""

    BATTERY_INCLUDED = "battery_included"
    BATTERY_LEASE = "battery_lease"


class PriceBookEntry(Base):
    """Giá niêm yết của một phiên bản theo một mô hình sở hữu."""

    __tablename__ = "pricing_price_book"

    id: Mapped[int] = mapped_column(primary_key=True)
    trim_id: Mapped[int] = mapped_column(ForeignKey("catalog_trim.id"))
    ownership_model: Mapped[OwnershipModel] = mapped_column(Enum(OwnershipModel))

    list_price_vnd: Mapped[int] = mapped_column(BigInteger)
    monthly_battery_fee_vnd: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class RegistrationFeeSchedule(Base):
    """Biểu phí lăn bánh theo tỉnh/thành.

    Lệ phí trước bạ và phí biển số khác nhau giữa các tỉnh — cùng một chiếc xe,
    hai tỉnh, hai con số. Đó là lý do bảng này khoá theo `province_code`.

    Các giá trị nạp sẵn trong `seed.py` là dữ liệu mẫu để chạy được, **chưa
    phải số liệu pháp lý đã đối chiếu**. Trước khi lên production phải thay
    bằng biểu phí chính thức.
    """

    __tablename__ = "pricing_registration_fee"

    id: Mapped[int] = mapped_column(primary_key=True)
    province_code: Mapped[str] = mapped_column(String(16))

    registration_tax_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4))
    plate_fee_vnd: Mapped[int] = mapped_column(BigInteger)
    inspection_fee_vnd: Mapped[int] = mapped_column(BigInteger)
    road_fee_year_vnd: Mapped[int] = mapped_column(BigInteger)
    civil_insurance_year_vnd: Mapped[int] = mapped_column(BigInteger)
    service_fee_vnd: Mapped[int] = mapped_column(BigInteger, default=0)

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class FuelType(enum.StrEnum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"


class FuelPriceReference(Base):
    """Giá nhiên liệu tham chiếu để so sánh chi phí vận hành với xe xăng dầu.

    Trang thật ghi rõ "cập nhật gần nhất ngày ..." — nghĩa là con số này là dữ
    liệu có mốc thời gian, không phải hằng số. Câu trả lời so sánh phải dẫn
    được ngày của giá đã dùng.
    """

    __tablename__ = "pricing_fuel_price"

    id: Mapped[int] = mapped_column(primary_key=True)
    fuel_type: Mapped[FuelType] = mapped_column(Enum(FuelType))
    region_code: Mapped[str] = mapped_column(String(16), default="V1")
    price_per_litre_vnd: Mapped[int] = mapped_column(BigInteger)

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)


class ElectricityPriceReference(Base):
    """Giá điện tham chiếu, dùng cho vế xe điện trong phép so sánh."""

    __tablename__ = "pricing_electricity_price"

    id: Mapped[int] = mapped_column(primary_key=True)
    region_code: Mapped[str] = mapped_column(String(16), default="V1")
    price_per_kwh_vnd: Mapped[int] = mapped_column(BigInteger)

    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
