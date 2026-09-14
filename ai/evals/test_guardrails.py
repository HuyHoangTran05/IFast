"""Eval cho bốn luật của R3.

Đây không phải unit test cho vui — mỗi test tương ứng một cách mà trợ lý AI có
thể nói sai về tiền hoặc thông số với khách mua xe.
"""

from __future__ import annotations

import inspect
from datetime import date

import pytest

from ai import tools as tools_module
from ai.ports import NotConfigured, UnconfiguredLlm
from ai.tools import MissingData, build_registry


class FakeApiClient:
    """Đóng vai `api/`. Trả None nghĩa là không có dữ liệu."""

    def __init__(self, **data):
        self._data = data

    def get_model(self, code):
        return self._data.get("model") if code == "VF2" else None

    def get_on_road(self, trim_id, province_code, as_of):
        return self._data.get("on_road") if province_code == "HN" else None

    def get_promotions(self, as_of):
        return self._data.get("promotions", [])

    def get_battery_compensation(self, serial, incident_on):
        return self._data.get("compensation") if serial == "PIN-001" else None


def test_khong_cong_cu_nao_tu_tinh_tien():
    """Luật 1 và 4: mọi phép tính tiền nằm trong api/, không nằm trong ai/.

    Quét mã nguồn của module công cụ: không được xuất hiện phép nhân chia trên
    Decimal hay bất kỳ dấu hiệu tính toán tiền nào.
    """
    source = inspect.getsource(tools_module)
    assert "Decimal" not in source
    assert "registration_tax_rate" not in source
    assert "* (1 -" not in source


def test_hoi_dong_xe_khong_ton_tai_thi_bao_khong_biet():
    """Luật 2: không đọc thông số từ trí nhớ model."""
    registry = build_registry(api_client=FakeApiClient())
    with pytest.raises(MissingData):
        registry["get_spec"].fn("VF999", date(2026, 6, 1))


def test_tinh_chua_co_bieu_phi_thi_bao_khong_biet_chu_khong_uoc_luong():
    registry = build_registry(api_client=FakeApiClient(on_road={"total_vnd": 1}))
    with pytest.raises(MissingData):
        registry["get_on_road_cost"].fn(1, "DN", date(2026, 6, 1))


def test_moi_ket_qua_deu_mang_theo_nguon():
    """Không có nguồn thì câu trả lời không được chứa con số."""
    registry = build_registry(api_client=FakeApiClient(model={"name": "VF 2"}))
    result = registry["get_spec"].fn("VF2", date(2026, 6, 1))
    assert result.source == "catalog/models/VF2"
    assert result.as_of == date(2026, 6, 1)


def test_uu_dai_phai_hoi_kem_moc_thoi_gian():
    """Luật 3: không tự suy ra ưu đãi còn hiệu lực."""
    registry = build_registry(api_client=FakeApiClient(promotions=[]))
    signature = inspect.signature(registry["get_active_promotions"].fn)
    assert "as_of" in signature.parameters


def test_boi_thuong_pin_lay_tu_api_khong_tu_tinh():
    registry = build_registry(
        api_client=FakeApiClient(compensation={"compensation_vnd": 75_000_000})
    )
    result = registry["get_battery_compensation"].fn("PIN-001", date(2028, 1, 1))
    assert result.value["compensation_vnd"] == 75_000_000
    assert result.source.startswith("battery/assets/")


def test_chua_cau_hinh_model_thi_tu_choi_chu_khong_bia():
    with pytest.raises(NotConfigured):
        UnconfiguredLlm().complete(system="", prompt="VF 2 giá bao nhiêu?")
