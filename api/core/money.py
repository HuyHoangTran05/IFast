"""Tiền tệ cho IFast.

VND không có phần thập phân, nên toàn hệ thống biểu diễn tiền bằng **số nguyên
đồng**. Không dùng float cho tiền ở bất kỳ đâu: 0.1 + 0.2 != 0.3 và sai số sẽ
tích luỹ qua các phép nhân phần trăm phí trước bạ.

Tỉ lệ (phần trăm phí, tỉ lệ khấu hao pin) dùng `Decimal`, và chỉ quy về số
nguyên đồng ở bước cuối cùng.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

Vnd = int


def to_vnd(value: Decimal | int) -> Vnd:
    """Quy một giá trị Decimal về số nguyên đồng, làm tròn nửa lên.

    Chỉ gọi ở bước cuối của một phép tính. Làm tròn ở từng bước trung gian sẽ
    tích luỹ sai lệch.
    """
    if isinstance(value, int):
        return value
    return int(Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def pct(amount: Vnd, rate: Decimal) -> Decimal:
    """Nhân một khoản tiền với một tỉ lệ, giữ nguyên độ chính xác Decimal."""
    return Decimal(amount) * rate
