"""Các phép tính tiền của IFast.

Mọi hàm ở đây nhận `as_of: date`. Không hàm nào mặc định về "hôm nay" — người
gọi phải nói rõ đang tính cho mốc thời gian nào, vì câu trả lời cho một đơn
hàng cũ khác câu trả lời cho một báo giá mới.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from api.core.effective import latest_effective_on
from api.core.money import Vnd, pct, to_vnd
from api.pricing.models import (
    ElectricityPriceReference,
    FuelPriceReference,
    OwnershipModel,
    PriceBookEntry,
    RegistrationFeeSchedule,
)


class PricingUnavailable(Exception):
    """Không có bảng giá hoặc biểu phí phủ mốc thời gian và địa bàn được hỏi.

    Ném lỗi thay vì trả 0. Một tỉnh chưa có biểu phí phải hiện "chưa hỗ trợ",
    không được hiện chi phí lăn bánh bằng đúng giá xe.
    """


@dataclass(frozen=True)
class LineItem:
    code: str
    label: str
    amount_vnd: Vnd


@dataclass(frozen=True)
class OnRoadQuote:
    """Dự toán chi phí lăn bánh, luôn kèm phần tách khoản.

    Khách nhìn thấy tổng, nhưng khi thắc mắc thì phải giải thích được từng
    khoản — nên tổng và phần tách khoản đi cùng nhau, không tách rời.
    """

    as_of: date
    province_code: str
    ownership_model: OwnershipModel
    vehicle_price_vnd: Vnd
    discount_vnd: Vnd
    items: tuple[LineItem, ...]
    total_vnd: Vnd
    monthly_battery_fee_vnd: Vnd | None

    @property
    def taxable_base_vnd(self) -> Vnd:
        return self.vehicle_price_vnd - self.discount_vnd


def resolve_price(
    entries: list[PriceBookEntry],
    trim_id: int,
    ownership_model: OwnershipModel,
    as_of: date,
) -> PriceBookEntry:
    matching = [e for e in entries if e.trim_id == trim_id and e.ownership_model == ownership_model]
    entry = latest_effective_on(matching, as_of)
    if entry is None:
        raise PricingUnavailable(
            f"không có giá cho trim={trim_id} mô hình={ownership_model.value} tại {as_of}"
        )
    return entry


def quote_on_road_cost(
    *,
    price_entry: PriceBookEntry,
    fee_schedules: list[RegistrationFeeSchedule],
    province_code: str,
    as_of: date,
    discount_vnd: Vnd = 0,
) -> OnRoadQuote:
    """Dự toán chi phí lăn bánh tại một tỉnh, ở một mốc thời gian.

    Lệ phí trước bạ tính trên giá **sau khi trừ ưu đãi**. Tính trên giá niêm
    yết sẽ khiến khách phải trả nhiều hơn thực tế.
    """
    schedules = [s for s in fee_schedules if s.province_code == province_code]
    schedule = latest_effective_on(schedules, as_of)
    if schedule is None:
        raise PricingUnavailable(f"chưa có biểu phí lăn bánh cho tỉnh {province_code} tại {as_of}")

    if discount_vnd < 0:
        raise ValueError("ưu đãi không thể âm")
    if discount_vnd > price_entry.list_price_vnd:
        raise ValueError("ưu đãi vượt quá giá xe")

    base = price_entry.list_price_vnd - discount_vnd
    registration_tax = to_vnd(pct(base, Decimal(schedule.registration_tax_rate)))

    items = (
        LineItem("vehicle", "Giá xe", base),
        LineItem("registration_tax", "Lệ phí trước bạ", registration_tax),
        LineItem("plate", "Phí đăng ký biển số", schedule.plate_fee_vnd),
        LineItem("inspection", "Phí đăng kiểm", schedule.inspection_fee_vnd),
        LineItem("road_fee", "Phí đường bộ (1 năm)", schedule.road_fee_year_vnd),
        LineItem("civil_insurance", "Bảo hiểm TNDS bắt buộc", schedule.civil_insurance_year_vnd),
        LineItem("service", "Phí dịch vụ đăng ký", schedule.service_fee_vnd),
    )

    return OnRoadQuote(
        as_of=as_of,
        province_code=province_code,
        ownership_model=price_entry.ownership_model,
        vehicle_price_vnd=price_entry.list_price_vnd,
        discount_vnd=discount_vnd,
        items=items,
        total_vnd=sum(i.amount_vnd for i in items),
        monthly_battery_fee_vnd=price_entry.monthly_battery_fee_vnd,
    )


@dataclass(frozen=True)
class RunningCostComparison:
    as_of: date
    monthly_km: int
    ev_monthly_cost_vnd: Vnd
    ice_monthly_cost_vnd: Vnd
    electricity_price_as_of: date
    fuel_price_as_of: date

    @property
    def monthly_saving_vnd(self) -> Vnd:
        return self.ice_monthly_cost_vnd - self.ev_monthly_cost_vnd


def compare_running_cost(
    *,
    monthly_km: int,
    ev_consumption_kwh_per_100km_x10: int,
    ice_consumption_litres_per_100km_x10: int,
    electricity_prices: list[ElectricityPriceReference],
    fuel_prices: list[FuelPriceReference],
    fuel_type,
    as_of: date,
    region_code: str = "V1",
) -> RunningCostComparison:
    """So sánh chi phí nhiên liệu hằng tháng giữa xe điện và xe động cơ đốt trong.

    Mức tiêu thụ nhận vào dưới dạng nhân 10 (ví dụ 6,5 lít/100km truyền vào
    65) để tránh dùng float cho dữ liệu người dùng nhập.

    Hàm trả kèm ngày hiệu lực của giá điện và giá nhiên liệu đã dùng: câu trả
    lời so sánh mà không nói dùng giá ngày nào thì không kiểm chứng được.
    """
    if monthly_km <= 0:
        raise ValueError("quãng đường mỗi tháng phải lớn hơn 0")

    electricity = latest_effective_on(
        [e for e in electricity_prices if e.region_code == region_code], as_of
    )
    if electricity is None:
        raise PricingUnavailable(f"chưa có giá điện tham chiếu cho {region_code} tại {as_of}")

    fuel = latest_effective_on(
        [f for f in fuel_prices if f.region_code == region_code and f.fuel_type == fuel_type],
        as_of,
    )
    if fuel is None:
        raise PricingUnavailable(f"chưa có giá nhiên liệu cho {region_code} tại {as_of}")

    hundreds = Decimal(monthly_km) / Decimal(100)
    ev_kwh = hundreds * Decimal(ev_consumption_kwh_per_100km_x10) / Decimal(10)
    ice_litres = hundreds * Decimal(ice_consumption_litres_per_100km_x10) / Decimal(10)

    return RunningCostComparison(
        as_of=as_of,
        monthly_km=monthly_km,
        ev_monthly_cost_vnd=to_vnd(ev_kwh * Decimal(electricity.price_per_kwh_vnd)),
        ice_monthly_cost_vnd=to_vnd(ice_litres * Decimal(fuel.price_per_litre_vnd)),
        electricity_price_as_of=electricity.effective_from,
        fuel_price_as_of=fuel.effective_from,
    )
