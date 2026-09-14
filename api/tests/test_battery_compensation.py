"""Công thức bồi thường pin thuê: B = A x (1 - T1/T2), sàn 10% của A.

Mỗi test ở đây tương ứng một cách làm sai rất tự nhiên mà lập trình viên hay
mắc. Đây không phải test cho có.
"""

from __future__ import annotations

from datetime import date

import pytest

from api.battery.models import BatteryListPrice, BatteryWarrantyPolicy
from api.battery.service import compute_compensation, months_of_use


class TestMonthRounding:
    """Luật làm tròn: từ 15 ngày tính tròn lên, dưới 15 ngày tính tròn xuống."""

    def test_tron_thang_chinh_xac(self):
        assert months_of_use(date(2026, 1, 10), date(2026, 4, 10)) == 3

    def test_du_14_ngay_thi_tron_xuong(self):
        assert months_of_use(date(2026, 1, 10), date(2026, 4, 24)) == 3

    def test_du_dung_15_ngay_thi_tron_len(self):
        assert months_of_use(date(2026, 1, 10), date(2026, 4, 25)) == 4

    def test_du_16_ngay_thi_tron_len(self):
        assert months_of_use(date(2026, 1, 10), date(2026, 4, 26)) == 4

    def test_cuoi_thang_khong_tran_sang_thang_sau(self):
        # 31/01 cộng một tháng phải ra 28/02, không phải 03/03.
        assert months_of_use(date(2026, 1, 31), date(2026, 2, 28)) == 1

    def test_su_co_truoc_khi_hinh_thanh_tai_san_la_loi(self):
        with pytest.raises(ValueError):
            months_of_use(date(2026, 5, 1), date(2026, 4, 30))


def _prices(*entries):
    return [BatteryListPrice(trim_id=None, price_vnd=p, effective_from=d) for p, d in entries]


def _policies(*entries):
    return [BatteryWarrantyPolicy(warranty_months=m, effective_from=d) for m, d in entries]


class TestCompensation:
    def test_cong_thuc_co_ban(self):
        # A = 100tr, T1 = 24 tháng, T2 = 96 tháng -> B = 100tr x (1 - 0,25) = 75tr
        result = compute_compensation(
            formed_on=date(2026, 1, 1),
            incident_on=date(2028, 1, 1),
            list_prices=_prices((100_000_000, date(2025, 1, 1))),
            warranty_policies=_policies((96, date(2025, 1, 1))),
        )
        assert result.months_used == 24
        assert result.warranty_months == 96
        assert result.compensation_vnd == 75_000_000
        assert result.floor_applied is False

    def test_gia_pin_lay_tai_thoi_diem_su_co_khong_phai_gia_luc_mua(self):
        """Cái bẫy thứ nhất: A tra tại thời điểm xảy ra sự cố."""
        result = compute_compensation(
            formed_on=date(2026, 1, 1),
            incident_on=date(2028, 1, 1),
            list_prices=_prices(
                (100_000_000, date(2025, 1, 1)),
                (120_000_000, date(2027, 6, 1)),  # tăng giá trước khi có sự cố
            ),
            warranty_policies=_policies((96, date(2025, 1, 1))),
        )
        assert result.list_price_vnd == 120_000_000
        assert result.list_price_as_of == date(2027, 6, 1)
        assert result.compensation_vnd == 90_000_000  # 120tr x 0,75

    def test_bao_hanh_lay_theo_chinh_sach_luc_hinh_thanh_tai_san(self):
        """Cái bẫy thứ hai: T2 tra tại thời điểm hình thành tài sản.

        Chính sách đổi từ 96 xuống 60 tháng sau khi pin đã hình thành. Pin này
        vẫn phải hưởng 96 tháng. Lấy nhầm 60 sẽ đòi khách trả nhiều hơn.
        """
        result = compute_compensation(
            formed_on=date(2026, 1, 1),
            incident_on=date(2028, 1, 1),
            list_prices=_prices((100_000_000, date(2025, 1, 1))),
            warranty_policies=_policies(
                (96, date(2025, 1, 1)),
                (60, date(2027, 1, 1)),  # siết chính sách sau khi pin đã hình thành
            ),
        )
        assert result.warranty_months == 96
        assert result.warranty_policy_as_of == date(2025, 1, 1)
        assert result.compensation_vnd == 75_000_000

    def test_hai_moc_thoi_gian_khac_nhau_trong_cung_mot_phep_tinh(self):
        """Cả hai cái bẫy cùng lúc — đây là ca sát thực tế nhất."""
        result = compute_compensation(
            formed_on=date(2026, 1, 1),
            incident_on=date(2028, 1, 1),
            list_prices=_prices(
                (100_000_000, date(2025, 1, 1)),
                (120_000_000, date(2027, 6, 1)),
            ),
            warranty_policies=_policies(
                (96, date(2025, 1, 1)),
                (60, date(2027, 1, 1)),
            ),
        )
        assert result.list_price_vnd == 120_000_000  # giá lúc sự cố
        assert result.warranty_months == 96  # bảo hành lúc hình thành tài sản
        assert result.compensation_vnd == 90_000_000

    def test_san_10_phan_tram_khi_gan_het_bao_hanh(self):
        """Cái bẫy thứ ba: thiếu sàn thì pin gần hết bảo hành ra gần 0 đồng."""
        result = compute_compensation(
            formed_on=date(2026, 1, 1),
            incident_on=date(2033, 11, 1),  # 94/96 tháng
            list_prices=_prices((100_000_000, date(2025, 1, 1))),
            warranty_policies=_policies((96, date(2025, 1, 1))),
        )
        assert result.floor_applied is True
        assert result.compensation_vnd == 10_000_000

    def test_qua_han_bao_hanh_khong_ra_so_am(self):
        result = compute_compensation(
            formed_on=date(2026, 1, 1),
            incident_on=date(2040, 1, 1),  # vượt xa 96 tháng
            list_prices=_prices((100_000_000, date(2025, 1, 1))),
            warranty_policies=_policies((96, date(2025, 1, 1))),
        )
        assert result.compensation_vnd == 10_000_000
        assert result.floor_applied is True

    def test_su_co_ngay_hom_hinh_thanh_thi_boi_thuong_toan_bo(self):
        result = compute_compensation(
            formed_on=date(2026, 1, 1),
            incident_on=date(2026, 1, 1),
            list_prices=_prices((100_000_000, date(2025, 1, 1))),
            warranty_policies=_policies((96, date(2025, 1, 1))),
        )
        assert result.months_used == 0
        assert result.compensation_vnd == 100_000_000
