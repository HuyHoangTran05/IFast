"""Luật chọn ưu đãi: có hiệu lực, khớp điều kiện, và kết quả phải tất định."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from api.promotions.models import Promotion, PromotionKind
from api.promotions.service import resolve_promotions

PRICE = 200_000_000


def _promo(code, **kw):
    base = dict(
        code=code,
        name=code,
        kind=PromotionKind.FIXED_AMOUNT,
        amount_vnd=10_000_000,
        percent=None,
        trim_id=None,
        province_code=None,
        ownership_model=None,
        priority=0,
        stackable=False,
        terms_url=None,
        effective_from=date(2026, 1, 1),
        effective_to=None,
    )
    base.update(kw)
    return Promotion(**base)


def _resolve(promos, as_of=date(2026, 6, 1), **kw):
    args = dict(
        trim_id=1,
        province_code="HN",
        ownership_model="battery_included",
        list_price_vnd=PRICE,
        as_of=as_of,
    )
    args.update(kw)
    return resolve_promotions(promos, **args)


class TestHieuLuc:
    def test_uu_dai_het_han_thi_thoi_ap_dung(self):
        promos = [_promo("HET-HAN", effective_to=date(2026, 3, 1))]
        assert _resolve(promos, as_of=date(2026, 6, 1)).total_discount_vnd == 0

    def test_uu_dai_chua_bat_dau_thi_chua_ap_dung(self):
        promos = [_promo("CHUA-CHAY", effective_from=date(2026, 12, 1))]
        assert _resolve(promos, as_of=date(2026, 6, 1)).total_discount_vnd == 0

    def test_ngay_bat_dau_la_ngay_da_co_hieu_luc(self):
        promos = [_promo("BAT-DAU", effective_from=date(2026, 6, 1))]
        assert _resolve(promos, as_of=date(2026, 6, 1)).total_discount_vnd == 10_000_000

    def test_ngay_ket_thuc_la_ngay_da_het_hieu_luc(self):
        promos = [_promo("KET-THUC", effective_to=date(2026, 6, 1))]
        assert _resolve(promos, as_of=date(2026, 6, 1)).total_discount_vnd == 0


class TestDieuKien:
    def test_khac_phien_ban_thi_khong_ap(self):
        assert _resolve([_promo("KHAC-TRIM", trim_id=999)]).total_discount_vnd == 0

    def test_khac_tinh_thi_khong_ap(self):
        assert _resolve([_promo("CHI-HCM", province_code="HCM")]).total_discount_vnd == 0

    def test_khac_mo_hinh_so_huu_thi_khong_ap(self):
        promos = [_promo("CHI-THUE-PIN", ownership_model="battery_lease")]
        assert _resolve(promos).total_discount_vnd == 0


class TestLuatUuTien:
    def test_hai_uu_dai_doc_quyen_chon_ben_uu_tien_cao_hon(self):
        promos = [
            _promo("THAP", priority=1, amount_vnd=30_000_000),
            _promo("CAO", priority=9, amount_vnd=20_000_000),
        ]
        outcome = _resolve(promos)
        assert [a.code for a in outcome.applied] == ["CAO"]
        assert outcome.total_discount_vnd == 20_000_000

    def test_uu_dai_doc_quyen_khong_cong_don_voi_ai(self):
        promos = [
            _promo("DOC-QUYEN", priority=9, amount_vnd=50_000_000, stackable=False),
            _promo("CONG-DON", amount_vnd=5_000_000, stackable=True),
        ]
        outcome = _resolve(promos)
        assert [a.code for a in outcome.applied] == ["DOC-QUYEN"]

    def test_chon_phuong_an_co_loi_hon_cho_khach(self):
        promos = [
            _promo("DOC-QUYEN", priority=9, amount_vnd=10_000_000, stackable=False),
            _promo("CD-1", amount_vnd=8_000_000, stackable=True),
            _promo("CD-2", amount_vnd=8_000_000, stackable=True),
        ]
        outcome = _resolve(promos)
        assert sorted(a.code for a in outcome.applied) == ["CD-1", "CD-2"]
        assert outcome.total_discount_vnd == 16_000_000

    def test_ket_qua_khong_phu_thuoc_thu_tu_dau_vao(self):
        """Tất định là yêu cầu bắt buộc: hai lần chạy phải ra một kết quả."""
        promos = [
            _promo("A", priority=5, amount_vnd=10_000_000),
            _promo("B", priority=5, amount_vnd=10_000_000),
            _promo("C", priority=5, amount_vnd=10_000_000),
        ]
        first = _resolve(promos)
        second = _resolve(list(reversed(promos)))
        assert [a.code for a in first.applied] == [a.code for a in second.applied]
        assert [a.code for a in first.applied] == ["A"]

    def test_uu_dai_hien_vat_giam_0_dong_nhung_van_duoc_liet_ke(self):
        promos = [
            _promo(
                "MIEN-PHI-SAC",
                kind=PromotionKind.BENEFIT_IN_KIND,
                amount_vnd=None,
                stackable=True,
                effective_from=date(2026, 2, 10),
            )
        ]
        outcome = _resolve(promos)
        assert [a.code for a in outcome.applied] == ["MIEN-PHI-SAC"]
        assert outcome.total_discount_vnd == 0

    def test_giam_theo_phan_tram(self):
        promos = [
            _promo(
                "GIAM-5",
                kind=PromotionKind.PERCENT_OF_PRICE,
                amount_vnd=None,
                percent=Decimal("0.05"),
            )
        ]
        assert _resolve(promos).total_discount_vnd == 10_000_000

    def test_giam_khong_bao_gio_vuot_gia_xe(self):
        promos = [_promo("QUA-TAY", amount_vnd=999_000_000_000)]
        assert _resolve(promos).total_discount_vnd == PRICE
