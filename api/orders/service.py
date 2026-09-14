"""Tạo đơn từ một bản dự toán, và khoá snapshot lại."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date

from api.core.money import Vnd
from api.orders.models import Order, OrderChannel, OrderStatus
from api.pricing.service import OnRoadQuote
from api.promotions.service import PromotionOutcome


class OrderImmutable(Exception):
    """Cố sửa snapshot của một đơn đã rời trạng thái nháp."""


def build_snapshot(quote: OnRoadQuote, promotions: PromotionOutcome) -> dict:
    """Đóng băng mọi thứ cần để giải thích lại con số này sau nhiều năm."""
    return {
        "as_of": quote.as_of.isoformat(),
        "province_code": quote.province_code,
        "ownership_model": quote.ownership_model.value,
        "vehicle_price_vnd": quote.vehicle_price_vnd,
        "discount_vnd": quote.discount_vnd,
        "monthly_battery_fee_vnd": quote.monthly_battery_fee_vnd,
        "items": [asdict(i) for i in quote.items],
        "total_vnd": quote.total_vnd,
        "promotions": [asdict(p) for p in promotions.applied],
    }


def create_order(
    *,
    code: str,
    trim_id: int,
    quote: OnRoadQuote,
    promotions: PromotionOutcome,
    deposit_vnd: Vnd,
    channel: OrderChannel = OrderChannel.DEPOSIT,
    customer_id: int | None = None,
) -> Order:
    if deposit_vnd < 0:
        raise ValueError("tiền cọc không thể âm")
    if deposit_vnd > quote.total_vnd:
        raise ValueError("tiền cọc không thể lớn hơn tổng giá trị đơn")

    return Order(
        code=code,
        customer_id=customer_id,
        channel=channel,
        status=OrderStatus.DEPOSIT_PENDING,
        trim_id=trim_id,
        province_code=quote.province_code,
        quoted_on=quote.as_of,
        price_snapshot=build_snapshot(quote, promotions),
        total_vnd=quote.total_vnd,
        deposit_vnd=deposit_vnd,
    )


def order_total_on(order: Order, _as_of: date) -> Vnd:
    """Tổng giá trị đơn, luôn đọc từ snapshot.

    Tham số thời gian có mặt để chỗ gọi không bị cám dỗ đi tra bảng giá. Câu
    trả lời không phụ thuộc vào nó — và đó chính là điều cần đảm bảo.
    """
    return order.total_vnd


def assert_snapshot_intact(order: Order, expected: dict) -> None:
    if order.status is not OrderStatus.DRAFT and order.price_snapshot != expected:
        raise OrderImmutable(f"snapshot của đơn {order.code} đã bị thay đổi")
