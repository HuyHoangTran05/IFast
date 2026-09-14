"""Dữ liệu mẫu để chạy được ngay.

Số liệu xe lấy từ trang VF 2 công khai của VinFast. Biểu phí lăn bánh, giá
điện và giá nhiên liệu là **dữ liệu mẫu hợp lý, chưa đối chiếu pháp lý** — đủ
để hệ thống chạy và để test, nhưng phải thay bằng biểu phí chính thức trước
khi lên production. Chỗ nào chưa chắc thì ghi rõ ở đây, không giả vờ là thật.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from api.battery.models import BatteryAsset, BatteryListPrice, BatteryWarrantyPolicy
from api.catalog.models import Color, ProductCategory, Spec, Trim, VehicleModel
from api.pricing.models import (
    ElectricityPriceReference,
    FuelPriceReference,
    FuelType,
    OwnershipModel,
    PriceBookEntry,
    RegistrationFeeSchedule,
)
from api.promotions.models import Promotion, PromotionKind

EPOCH = date(2026, 1, 1)


def seed(session: Session) -> None:
    vf2 = VehicleModel(
        code="VF2",
        name="VinFast VF 2",
        category=ProductCategory.CAR,
        segment="MiniCar",
        seats=4,
    )
    session.add(vf2)
    session.flush()

    trim = Trim(model_id=vf2.id, code="VF2-STD", name="VF 2 Tiêu chuẩn")
    session.add(trim)
    session.flush()

    # Thông số công bố trên trang VF 2.
    session.add(
        Spec(
            trim_id=trim.id,
            motor_count=1,
            max_power_w=30_000,
            max_torque_nm=65,
            range_nedc_km=210,
            fast_charge_minutes=34,
            drivetrain="RWD",
            consumption_kwh_per_100km_x10=120,  # dữ liệu mẫu, chưa công bố chính thức
        )
    )
    session.add_all(
        [
            Color(model_id=vf2.id, code="URBANT_MINT", name="Urbant Mint"),
            Color(model_id=vf2.id, code="BLACK", name="Đen"),
        ]
    )

    # Giá công bố: 188.000.000 niêm yết, 178.600.000 sau ưu đãi (kèm pin).
    session.add_all(
        [
            PriceBookEntry(
                trim_id=trim.id,
                ownership_model=OwnershipModel.BATTERY_INCLUDED,
                list_price_vnd=188_000_000,
                effective_from=EPOCH,
            ),
            PriceBookEntry(
                trim_id=trim.id,
                ownership_model=OwnershipModel.BATTERY_LEASE,
                list_price_vnd=148_000_000,  # dữ liệu mẫu
                monthly_battery_fee_vnd=1_400_000,  # dữ liệu mẫu
                effective_from=EPOCH,
            ),
        ]
    )

    # Biểu phí mẫu. Xe điện chạy pin đang hưởng lệ phí trước bạ 0% theo chính
    # sách hiện hành — mô hình hoá bằng một dòng có hạn hiệu lực, không hardcode.
    session.add_all(
        [
            RegistrationFeeSchedule(
                province_code="HN",
                registration_tax_rate=Decimal("0.0000"),
                plate_fee_vnd=20_000_000,
                inspection_fee_vnd=340_000,
                road_fee_year_vnd=1_560_000,
                civil_insurance_year_vnd=480_700,
                service_fee_vnd=2_000_000,
                effective_from=EPOCH,
                effective_to=date(2027, 3, 1),
            ),
            RegistrationFeeSchedule(
                province_code="HN",
                registration_tax_rate=Decimal("0.0600"),
                plate_fee_vnd=20_000_000,
                inspection_fee_vnd=340_000,
                road_fee_year_vnd=1_560_000,
                civil_insurance_year_vnd=480_700,
                service_fee_vnd=2_000_000,
                effective_from=date(2027, 3, 1),
            ),
            RegistrationFeeSchedule(
                province_code="HCM",
                registration_tax_rate=Decimal("0.0000"),
                plate_fee_vnd=11_000_000,
                inspection_fee_vnd=340_000,
                road_fee_year_vnd=1_560_000,
                civil_insurance_year_vnd=480_700,
                service_fee_vnd=2_000_000,
                effective_from=EPOCH,
                effective_to=date(2027, 3, 1),
            ),
        ]
    )

    # Giá nhiên liệu tham chiếu, theo mốc công bố trên trang so sánh.
    session.add_all(
        [
            FuelPriceReference(
                fuel_type=FuelType.GASOLINE,
                price_per_litre_vnd=22_600,
                effective_from=date(2026, 8, 27),
            ),
            FuelPriceReference(
                fuel_type=FuelType.DIESEL,
                price_per_litre_vnd=29_880,
                effective_from=date(2026, 8, 27),
            ),
            ElectricityPriceReference(price_per_kwh_vnd=3_000, effective_from=EPOCH),
        ]
    )

    session.add_all(
        [
            Promotion(
                code="VF2-LAUNCH",
                name="Ưu đãi ra mắt VF 2",
                kind=PromotionKind.FIXED_AMOUNT,
                amount_vnd=9_400_000,
                trim_id=trim.id,
                priority=100,
                stackable=False,
                effective_from=EPOCH,
            ),
            Promotion(
                code="FREE-CHARGING-2026",
                name="Miễn phí sạc",
                kind=PromotionKind.BENEFIT_IN_KIND,
                priority=10,
                stackable=True,
                effective_from=date(2026, 2, 10),
            ),
        ]
    )

    session.add_all(
        [
            BatteryWarrantyPolicy(warranty_months=96, effective_from=EPOCH),
            BatteryListPrice(trim_id=trim.id, price_vnd=90_000_000, effective_from=EPOCH),
            # Một pin thuê mẫu để endpoint bồi thường dùng được ngay.
            BatteryAsset(serial="PIN-VF2-0001", trim_id=trim.id, formed_on=date(2026, 1, 1)),
        ]
    )
    session.commit()
