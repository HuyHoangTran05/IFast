"""Dự toán chi phí lăn bánh và so sánh chi phí vận hành."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from api.pricing.models import (
    ElectricityPriceReference,
    FuelPriceReference,
    FuelType,
    OwnershipModel,
    PriceBookEntry,
    RegistrationFeeSchedule,
)
from api.pricing.service import (
    PricingUnavailable,
    compare_running_cost,
    quote_on_road_cost,
    resolve_price,
)


def _price(**kw):
    base = dict(
        trim_id=1,
        ownership_model=OwnershipModel.BATTERY_INCLUDED,
        list_price_vnd=188_000_000,
        effective_from=date(2026, 1, 1),
        effective_to=None,
        monthly_battery_fee_vnd=None,
    )
    base.update(kw)
    return PriceBookEntry(**base)


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


class TestOnRoadCost:
    def test_cung_mot_xe_hai_tinh_ra_hai_con_so(self):
        """Phí biển số khác nhau theo tỉnh — đây là lý do bảng phí khoá theo tỉnh."""
        schedules = [
            _schedule(province_code="HN", plate_fee_vnd=20_000_000),
            _schedule(province_code="HCM", plate_fee_vnd=11_000_000),
        ]
        hn = quote_on_road_cost(
            price_entry=_price(),
            fee_schedules=schedules,
            province_code="HN",
            as_of=date(2026, 6, 1),
        )
        hcm = quote_on_road_cost(
            price_entry=_price(),
            fee_schedules=schedules,
            province_code="HCM",
            as_of=date(2026, 6, 1),
        )
        assert hn.total_vnd - hcm.total_vnd == 9_000_000

    def test_le_phi_truoc_ba_tinh_tren_gia_sau_uu_dai(self):
        """Tính trên giá niêm yết sẽ bắt khách trả nhiều hơn thực tế."""
        quote = quote_on_road_cost(
            price_entry=_price(list_price_vnd=200_000_000),
            fee_schedules=[_schedule(registration_tax_rate=Decimal("0.1000"))],
            province_code="HN",
            as_of=date(2026, 6, 1),
            discount_vnd=20_000_000,
        )
        tax = next(i for i in quote.items if i.code == "registration_tax")
        assert tax.amount_vnd == 18_000_000  # 10% của 180tr, không phải của 200tr

    def test_bieu_phi_doi_theo_ngay_hieu_luc(self):
        """Cùng một tỉnh, hai mốc thời gian, hai mức thuế."""
        schedules = [
            _schedule(
                registration_tax_rate=Decimal("0.0000"),
                effective_from=date(2026, 1, 1),
                effective_to=date(2027, 3, 1),
            ),
            _schedule(
                registration_tax_rate=Decimal("0.0600"),
                effective_from=date(2027, 3, 1),
            ),
        ]
        truoc = quote_on_road_cost(
            price_entry=_price(),
            fee_schedules=schedules,
            province_code="HN",
            as_of=date(2026, 6, 1),
        )
        sau = quote_on_road_cost(
            price_entry=_price(),
            fee_schedules=schedules,
            province_code="HN",
            as_of=date(2027, 6, 1),
        )
        assert truoc.total_vnd < sau.total_vnd
        assert sau.total_vnd - truoc.total_vnd == 11_280_000  # 6% của 188tr

    def test_tinh_chua_co_bieu_phi_thi_bao_loi_chu_khong_tra_ve_khong(self):
        """Trả 0 sẽ khiến trang hiện giá lăn bánh đúng bằng giá xe."""
        with pytest.raises(PricingUnavailable):
            quote_on_road_cost(
                price_entry=_price(),
                fee_schedules=[_schedule(province_code="HN")],
                province_code="DN",
                as_of=date(2026, 6, 1),
            )

    def test_tong_bang_dung_tong_cac_khoan(self):
        quote = quote_on_road_cost(
            price_entry=_price(),
            fee_schedules=[_schedule()],
            province_code="HN",
            as_of=date(2026, 6, 1),
        )
        assert quote.total_vnd == sum(i.amount_vnd for i in quote.items)

    def test_uu_dai_vuot_gia_xe_la_loi(self):
        with pytest.raises(ValueError):
            quote_on_road_cost(
                price_entry=_price(list_price_vnd=100_000_000),
                fee_schedules=[_schedule()],
                province_code="HN",
                as_of=date(2026, 6, 1),
                discount_vnd=200_000_000,
            )


class TestOwnershipModel:
    def test_kem_pin_va_thue_pin_la_hai_bien_the_gia_khac_nhau(self):
        entries = [
            _price(ownership_model=OwnershipModel.BATTERY_INCLUDED, list_price_vnd=188_000_000),
            _price(
                ownership_model=OwnershipModel.BATTERY_LEASE,
                list_price_vnd=148_000_000,
                monthly_battery_fee_vnd=1_400_000,
            ),
        ]
        kem = resolve_price(entries, 1, OwnershipModel.BATTERY_INCLUDED, date(2026, 6, 1))
        thue = resolve_price(entries, 1, OwnershipModel.BATTERY_LEASE, date(2026, 6, 1))

        assert kem.list_price_vnd != thue.list_price_vnd
        assert kem.monthly_battery_fee_vnd is None
        assert thue.monthly_battery_fee_vnd == 1_400_000

    def test_thue_pin_giu_phi_hang_thang_trong_ban_du_toan(self):
        quote = quote_on_road_cost(
            price_entry=_price(
                ownership_model=OwnershipModel.BATTERY_LEASE,
                monthly_battery_fee_vnd=1_400_000,
            ),
            fee_schedules=[_schedule()],
            province_code="HN",
            as_of=date(2026, 6, 1),
        )
        assert quote.monthly_battery_fee_vnd == 1_400_000


class TestRunningCost:
    def test_so_sanh_kem_theo_ngay_cua_gia_da_dung(self):
        """Không dẫn được ngày của giá thì không kiểm chứng được con số."""
        result = compare_running_cost(
            monthly_km=1_000,
            ev_consumption_kwh_per_100km_x10=120,  # 12,0 kWh/100km
            ice_consumption_litres_per_100km_x10=65,  # 6,5 lít/100km
            electricity_prices=[
                ElectricityPriceReference(
                    region_code="V1", price_per_kwh_vnd=3_000, effective_from=date(2026, 1, 1)
                )
            ],
            fuel_prices=[
                FuelPriceReference(
                    fuel_type=FuelType.GASOLINE,
                    region_code="V1",
                    price_per_litre_vnd=22_600,
                    effective_from=date(2026, 8, 27),
                )
            ],
            fuel_type=FuelType.GASOLINE,
            as_of=date(2026, 9, 1),
        )
        assert result.ev_monthly_cost_vnd == 360_000  # 120 kWh x 3.000
        assert result.ice_monthly_cost_vnd == 1_469_000  # 65 lít x 22.600
        assert result.monthly_saving_vnd == 1_109_000
        assert result.fuel_price_as_of == date(2026, 8, 27)

    def test_quang_duong_khong_hop_le(self):
        with pytest.raises(ValueError):
            compare_running_cost(
                monthly_km=0,
                ev_consumption_kwh_per_100km_x10=120,
                ice_consumption_litres_per_100km_x10=65,
                electricity_prices=[],
                fuel_prices=[],
                fuel_type=FuelType.GASOLINE,
                as_of=date(2026, 9, 1),
            )
