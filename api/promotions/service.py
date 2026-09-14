"""Chọn ra tập ưu đãi áp dụng và tính số tiền giảm.

Nhiều ưu đãi cùng hợp lệ là chuyện bình thường. Điều không được phép là hai
lần gọi cùng dữ liệu lại ra hai kết quả khác nhau — nên luật ưu tiên ở đây
được định nghĩa tường minh và có tie-break đến tận cùng.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from api.core.effective import is_effective_on
from api.core.money import Vnd, pct, to_vnd
from api.promotions.models import Promotion, PromotionKind


@dataclass(frozen=True)
class AppliedPromotion:
    code: str
    name: str
    discount_vnd: Vnd
    terms_url: str | None


@dataclass(frozen=True)
class PromotionOutcome:
    applied: tuple[AppliedPromotion, ...]
    total_discount_vnd: Vnd


def _matches(promo: Promotion, *, trim_id: int, province_code: str, ownership_model: str) -> bool:
    if promo.trim_id is not None and promo.trim_id != trim_id:
        return False
    if promo.province_code is not None and promo.province_code != province_code:
        return False
    if promo.ownership_model is not None and promo.ownership_model != ownership_model:
        return False
    return True


def _discount_of(promo: Promotion, list_price_vnd: Vnd) -> Vnd:
    if promo.kind is PromotionKind.FIXED_AMOUNT:
        return min(promo.amount_vnd or 0, list_price_vnd)
    if promo.kind is PromotionKind.PERCENT_OF_PRICE:
        return min(to_vnd(pct(list_price_vnd, Decimal(promo.percent or 0))), list_price_vnd)
    return 0


def resolve_promotions(
    promotions: list[Promotion],
    *,
    trim_id: int,
    province_code: str,
    ownership_model: str,
    list_price_vnd: Vnd,
    as_of: date,
) -> PromotionOutcome:
    """Luật ưu tiên, theo đúng thứ tự:

    1. Loại bỏ ưu đãi không còn hiệu lực tại `as_of` và ưu đãi không khớp điều
       kiện (phiên bản, tỉnh, mô hình sở hữu).
    2. Chia phần còn lại làm hai nhóm: cộng dồn được và không cộng dồn.
    3. Phương án A là ưu đãi không cộng dồn tốt nhất, đứng **một mình**.
       Phương án B là tổng của toàn bộ ưu đãi cộng dồn được.
    4. Chọn phương án có lợi hơn cho khách. Bằng nhau thì chọn A.

    "Tốt nhất" trong bước 3 là ưu tiên cao hơn trước, rồi mới đến số tiền giảm
    lớn hơn, rồi đến mã ưu đãi theo thứ tự chữ cái. Tie-break tới tận mã để hai
    lần chạy không bao giờ ra hai kết quả khác nhau.

    Ưu đãi hiện vật (miễn phí sạc) giảm 0 đồng nhưng vẫn được liệt kê, vì khách
    cần thấy nó và nó vẫn kèm điều khoản riêng.
    """
    eligible = [
        p
        for p in promotions
        if is_effective_on(p, as_of)
        and _matches(
            p, trim_id=trim_id, province_code=province_code, ownership_model=ownership_model
        )
    ]

    def to_applied(p: Promotion) -> AppliedPromotion:
        return AppliedPromotion(p.code, p.name, _discount_of(p, list_price_vnd), p.terms_url)

    exclusive = [p for p in eligible if not p.stackable]
    stackable = [p for p in eligible if p.stackable]

    best_exclusive = None
    if exclusive:
        best_exclusive = max(
            exclusive,
            key=lambda p: (p.priority, _discount_of(p, list_price_vnd), _reverse_code(p.code)),
        )

    option_a = (to_applied(best_exclusive),) if best_exclusive else ()
    option_b = tuple(to_applied(p) for p in sorted(stackable, key=lambda p: p.code))

    total_a = sum(a.discount_vnd for a in option_a)
    total_b = sum(a.discount_vnd for a in option_b)

    if option_a and total_a >= total_b:
        chosen, total = option_a, total_a
    else:
        chosen, total = option_b, total_b

    return PromotionOutcome(applied=chosen, total_discount_vnd=min(total, list_price_vnd))


def _reverse_code(code: str) -> tuple[int, ...]:
    """Khoá phụ để mã nhỏ hơn theo chữ cái được ưu tiên khi mọi thứ khác bằng nhau."""
    return tuple(-ord(c) for c in code)
