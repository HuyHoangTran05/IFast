"""Bất biến snapshot: đơn đã chốt không đổi khi bảng giá đổi.

Đây là ranh giới giữa R2a và R2b. Nếu bất biến này vỡ thì không chỉ sai nghiệp
vụ — hai người backend sẽ bắt đầu phải chờ nhau.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from api.orders.models import OrderStatus
from api.orders.service import create_order, order_total_on
from api.pricing.models import OwnershipModel, PriceBookEntry, RegistrationFeeSchedule
from api.pricing.service import quote_on_road_cost, resolve_price
from api.promotions.models import Promotion, PromotionKind
from api.promotions.service import resolve_promotions

AS_OF = date(2026, 6, 1)


def _schedule(**kw):
    base = dict(
        province_code="HN",
        registration_tax_rate=Decimal("0.0000"),
        plate_fee_vnd=20_000_000,
        inspection_fee_vnd=340_000,
        road_fee_year_vnd=1_560_000,
        civil_insurance_year_vnd=480_700,
        service_fee_vnd=2_000_000,
        effective_from=date(2026, 1, 1),
        effective_to=None,
    )
    base.update(kw)
    return RegistrationFeeSchedule(**base)


def _make_order(prices, promos, schedules, as_of=AS_OF, code="DH-001"):
    price = resolve_price(prices, 1, OwnershipModel.BATTERY_INCLUDED, as_of)
    outcome = resolve_promotions(
        promos,
        trim_id=1,
        province_code="HN",
        ownership_model="battery_included",
        list_price_vnd=price.list_price_vnd,
        as_of=as_of,
    )
    quote = quote_on_road_cost(
        price_entry=price,
        fee_schedules=schedules,
        province_code="HN",
        as_of=as_of,
        discount_vnd=outcome.total_discount_vnd,
    )
    return create_order(
        code=code, trim_id=1, quote=quote, promotions=outcome, deposit_vnd=10_000_000
    )


def test_bang_gia_doi_sau_khong_lam_doi_don_da_chot():
    prices = [
        PriceBookEntry(
            trim_id=1,
            ownership_model=OwnershipModel.BATTERY_INCLUDED,
            list_price_vnd=188_000_000,
            effective_from=date(2026, 1, 1),
        )
    ]
    order = _make_order(prices, [], [_schedule()])
    total_luc_chot = order.total_vnd

    # R2a tăng giá sau khi đơn đã chốt.
    prices.append(
        PriceBookEntry(
            trim_id=1,
            ownership_model=OwnershipModel.BATTERY_INCLUDED,
            list_price_vnd=220_000_000,
            effective_from=date(2026, 7, 1),
        )
    )

    assert order.total_vnd == total_luc_chot
    assert order_total_on(order, date(2027, 1, 1)) == total_luc_chot
    assert order.price_snapshot["vehicle_price_vnd"] == 188_000_000


def test_uu_dai_het_han_sau_do_khong_bi_go_khoi_don():
    prices = [
        PriceBookEntry(
            trim_id=1,
            ownership_model=OwnershipModel.BATTERY_INCLUDED,
            list_price_vnd=188_000_000,
            effective_from=date(2026, 1, 1),
        )
    ]
    promos = [
        Promotion(
            code="VF2-LAUNCH",
            name="Ưu đãi ra mắt",
            kind=PromotionKind.FIXED_AMOUNT,
            amount_vnd=9_400_000,
            priority=100,
            stackable=False,
            effective_from=date(2026, 1, 1),
            effective_to=date(2026, 9, 1),
        )
    ]
    order = _make_order(prices, promos, [_schedule()])

    assert order.price_snapshot["discount_vnd"] == 9_400_000
    assert [p["code"] for p in order.price_snapshot["promotions"]] == ["VF2-LAUNCH"]
    # Ưu đãi hết hạn 01/09 nhưng đơn ký 01/06 vẫn giữ nguyên căn cứ.
    assert order.price_snapshot["as_of"] == "2026-06-01"


def test_snapshot_giu_du_can_cu_de_giai_thich_lai():
    prices = [
        PriceBookEntry(
            trim_id=1,
            ownership_model=OwnershipModel.BATTERY_INCLUDED,
            list_price_vnd=188_000_000,
            effective_from=date(2026, 1, 1),
        )
    ]
    order = _make_order(prices, [], [_schedule()])
    snap = order.price_snapshot

    assert snap["province_code"] == "HN"
    assert snap["ownership_model"] == "battery_included"
    assert {i["code"] for i in snap["items"]} >= {
        "vehicle",
        "registration_tax",
        "plate",
        "inspection",
        "road_fee",
        "civil_insurance",
    }
    assert snap["total_vnd"] == sum(i["amount_vnd"] for i in snap["items"])


def test_don_moi_tao_cho_thanh_toan_coc():
    prices = [
        PriceBookEntry(
            trim_id=1,
            ownership_model=OwnershipModel.BATTERY_INCLUDED,
            list_price_vnd=188_000_000,
            effective_from=date(2026, 1, 1),
        )
    ]
    order = _make_order(prices, [], [_schedule()])
    assert order.status is OrderStatus.DEPOSIT_PENDING
    assert order.deposit_vnd == 10_000_000
