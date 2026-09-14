"""Tập công cụ mà mô hình được phép gọi.

Bốn luật của R3 (xem `.claude/agents/r3-ai.md`) được cơ chế hoá ở đây thay vì
chỉ viết trong prompt: mọi con số đều đi qua một công cụ có nguồn, và mỗi kết
quả mang theo căn cứ để dẫn lại.

Điều quan trọng nhất trong file này là thứ **không** có: không có hàm nào tự
tính tiền. Mọi phép tính tiền nằm trong `api/`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Callable


@dataclass(frozen=True)
class ToolResult:
    """Kết quả kèm nguồn.

    `source` phải trỏ về bản ghi cụ thể đã dùng. Không có nguồn thì câu trả lời
    không được phép chứa con số.
    """

    value: Any
    source: str
    as_of: date


class MissingData(Exception):
    """Không có dữ liệu cho câu hỏi. Phải nói không biết, không được suy đoán."""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    fn: Callable[..., ToolResult]


def build_registry(*, api_client) -> dict[str, Tool]:
    """Đăng ký công cụ. `api_client` là cổng duy nhất ra `api/`.

    `ai/` chỉ nói chuyện với `api/`. Không truy vấn CSDL trực tiếp, không nhớ
    thông số, không tự tính.
    """

    def get_spec(model_code: str, as_of: date) -> ToolResult:
        data = api_client.get_model(model_code)
        if data is None:
            raise MissingData(f"không có dòng xe {model_code}")
        return ToolResult(data, f"catalog/models/{model_code}", as_of)

    def get_on_road_cost(trim_id: int, province_code: str, as_of: date) -> ToolResult:
        data = api_client.get_on_road(trim_id, province_code, as_of)
        if data is None:
            raise MissingData(f"chưa có biểu phí cho tỉnh {province_code}")
        return ToolResult(data, f"pricing/on-road?province={province_code}", as_of)

    def get_active_promotions(as_of: date) -> ToolResult:
        return ToolResult(api_client.get_promotions(as_of), "promotions", as_of)

    def get_battery_compensation(serial: str, incident_on: date) -> ToolResult:
        data = api_client.get_battery_compensation(serial, incident_on)
        if data is None:
            raise MissingData(f"không có pin số {serial}")
        return ToolResult(data, f"battery/assets/{serial}/compensation", incident_on)

    tools = [
        Tool("get_spec", "Thông số kỹ thuật của một dòng xe", get_spec),
        Tool("get_on_road_cost", "Dự toán chi phí lăn bánh theo tỉnh", get_on_road_cost),
        Tool(
            "get_active_promotions",
            "Ưu đãi còn hiệu lực tại một mốc thời gian",
            get_active_promotions,
        ),
        Tool(
            "get_battery_compensation",
            "Bồi thường pin thuê theo công thức chính thức",
            get_battery_compensation,
        ),
    ]
    return {t.name: t for t in tools}
