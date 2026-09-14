"""Bồi thường pin thuê.

Đặc tả lấy từ trang dịch vụ pin của VinFast:

    B = A × (1 − T1 / T2)

    B  giá trị bồi thường
    A  giá pin công bố **tại thời điểm xảy ra sự cố**
    T1 thời gian sử dụng, tính tròn theo tháng: từ 15 ngày tính tròn lên,
       dưới 15 ngày tính tròn xuống
    T2 thời gian bảo hành theo chính sách **tại thời điểm hình thành tài sản**

    Mức bồi thường B không được thấp hơn 10% giá công bố A.

Ba cái bẫy nằm gọn trong một công thức:

1. `A` và `T2` tra ở **hai mốc thời gian khác nhau**. Dùng chính sách hiện
   hành cho cả hai là tính sai tiền của khách.
2. Luật làm tròn 15 ngày. Làm tròn sai lệch nguyên một tháng khấu hao.
3. Sàn 10%. Thiếu nó thì pin gần hết bảo hành ra bồi thường gần bằng không, và
   pin quá hạn bảo hành ra số âm.

Trường hợp pin còn sửa được thì **không dùng công thức này** — thanh toán theo
báo giá thực tế của xưởng dịch vụ.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from api.battery.models import BatteryListPrice, BatteryWarrantyPolicy
from api.core.effective import latest_effective_on
from api.core.money import Vnd, to_vnd

MINIMUM_COMPENSATION_RATE = Decimal("0.10")
ROUND_UP_FROM_DAYS = 15


class BatteryPolicyUnavailable(Exception):
    """Thiếu giá pin công bố hoặc chính sách bảo hành ở mốc thời gian cần tra."""


def _add_months(start: date, months: int) -> date:
    """Cộng tháng, kẹp về ngày cuối tháng khi tháng đích ngắn hơn.

    31/01 cộng 1 tháng ra 28/02, không tràn sang tháng 3.
    """
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def months_of_use(formed_on: date, incident_on: date) -> int:
    """Thời gian sử dụng tính tròn theo tháng, theo luật 15 ngày.

    Đếm số tháng tròn đã trôi qua, rồi xét phần dư: từ 15 ngày trở lên tính
    thêm một tháng, dưới 15 ngày bỏ.
    """
    if incident_on < formed_on:
        raise ValueError("thời điểm xảy ra sự cố không thể trước thời điểm hình thành tài sản")

    months = (incident_on.year - formed_on.year) * 12 + (incident_on.month - formed_on.month)
    if _add_months(formed_on, months) > incident_on:
        months -= 1

    remainder_days = (incident_on - _add_months(formed_on, months)).days
    if remainder_days >= ROUND_UP_FROM_DAYS:
        months += 1
    return months


@dataclass(frozen=True)
class CompensationBreakdown:
    """Kết quả kèm toàn bộ đầu vào đã dùng.

    Đây là số tiền đòi khách hàng trả, nên phải giải thích được: giá nào, ngày
    nào, chính sách nào, và có bị chặn bởi sàn 10% hay không.
    """

    compensation_vnd: Vnd
    list_price_vnd: Vnd
    list_price_as_of: date
    months_used: int
    warranty_months: int
    warranty_policy_as_of: date
    floor_applied: bool

    @property
    def depreciation_ratio(self) -> Decimal:
        return Decimal(self.months_used) / Decimal(self.warranty_months)


def compute_compensation(
    *,
    formed_on: date,
    incident_on: date,
    list_prices: list[BatteryListPrice],
    warranty_policies: list[BatteryWarrantyPolicy],
    trim_id: int | None = None,
) -> CompensationBreakdown:
    """Tính B = A × (1 − T1/T2), có sàn 10% của A."""
    candidates = [p for p in list_prices if p.trim_id in (None, trim_id)]
    price = latest_effective_on(candidates, incident_on)
    if price is None:
        raise BatteryPolicyUnavailable(f"chưa có giá pin công bố tại {incident_on}")

    policy = latest_effective_on(warranty_policies, formed_on)
    if policy is None:
        raise BatteryPolicyUnavailable(f"chưa có chính sách bảo hành pin tại {formed_on}")
    if policy.warranty_months <= 0:
        raise ValueError("thời gian bảo hành phải lớn hơn 0")

    t1 = months_of_use(formed_on, incident_on)
    t2 = policy.warranty_months
    a = price.price_vnd

    raw = Decimal(a) * (Decimal(1) - Decimal(t1) / Decimal(t2))
    floor = Decimal(a) * MINIMUM_COMPENSATION_RATE

    floor_applied = raw < floor
    return CompensationBreakdown(
        compensation_vnd=to_vnd(floor if floor_applied else raw),
        list_price_vnd=a,
        list_price_as_of=price.effective_from,
        months_used=t1,
        warranty_months=t2,
        warranty_policy_as_of=policy.effective_from,
        floor_applied=floor_applied,
    )
