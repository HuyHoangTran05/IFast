"""Danh mục sản phẩm.

Thông số kỹ thuật phải **có kiểu dữ liệu**, không phải chuỗi tự do: `ai/` đọc
từ đây để trả lời khách, và một con số sai trong câu trả lời về xe là rủi ro
pháp lý chứ không phải lỗi hiển thị.

`ProductCategory` tồn tại ngay từ đầu vì VinFast bán cả ô tô lẫn xe máy điện,
và hai loại đo bằng đơn vị khác nhau (ô tô: kW và km NEDC; xe máy: W và km mỗi
lần sạc). Thêm loại sản phẩm sau khi đã có dữ liệu thật thì rất đắt.
"""

from __future__ import annotations

import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.db import Base


class ProductCategory(str, enum.Enum):
    CAR = "car"
    MOTORBIKE = "motorbike"


class VehicleModel(Base):
    """Một dòng xe, ví dụ VF 2."""

    __tablename__ = "catalog_vehicle_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(128))
    category: Mapped[ProductCategory] = mapped_column(Enum(ProductCategory))
    segment: Mapped[str | None] = mapped_column(String(64), nullable=True)
    seats: Mapped[int | None] = mapped_column(Integer, nullable=True)

    trims: Mapped[list["Trim"]] = relationship(back_populates="model")
    colors: Mapped[list["Color"]] = relationship(back_populates="model")


class Trim(Base):
    """Phiên bản của một dòng xe. Giá gắn với phiên bản, không gắn với dòng."""

    __tablename__ = "catalog_trim"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("catalog_vehicle_model.id"))
    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(128))

    model: Mapped[VehicleModel] = relationship(back_populates="trims")
    spec: Mapped["Spec | None"] = relationship(back_populates="trim", uselist=False)

    __table_args__ = (UniqueConstraint("model_id", "code"),)


class Color(Base):
    __tablename__ = "catalog_color"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("catalog_vehicle_model.id"))
    code: Mapped[str] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(128))
    exterior: Mapped[bool] = mapped_column(default=True)

    model: Mapped[VehicleModel] = relationship(back_populates="colors")

    __table_args__ = (UniqueConstraint("model_id", "code", "exterior"),)


class Spec(Base):
    """Thông số kỹ thuật, mỗi đại lượng một cột có kiểu và có đơn vị rõ ràng.

    Cho phép NULL vì ô tô và xe máy không dùng chung tập đại lượng. Không bao
    giờ nhét thông số vào một cột text.
    """

    __tablename__ = "catalog_spec"

    id: Mapped[int] = mapped_column(primary_key=True)
    trim_id: Mapped[int] = mapped_column(ForeignKey("catalog_trim.id"), unique=True)

    motor_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_power_w: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_torque_nm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    range_nedc_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    range_per_charge_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fast_charge_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    top_speed_kmh: Mapped[int | None] = mapped_column(Integer, nullable=True)
    drivetrain: Mapped[str | None] = mapped_column(String(32), nullable=True)
    battery_capacity_kwh_x10: Mapped[int | None] = mapped_column(Integer, nullable=True)
    consumption_kwh_per_100km_x10: Mapped[int | None] = mapped_column(Integer, nullable=True)

    trim: Mapped[Trim] = relationship(back_populates="spec")
