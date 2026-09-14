"""Tra cứu chính sách theo thời điểm hiệu lực.

Bất biến số 1 của IFast: mọi bảng giá và bảng chính sách đều có ngày hiệu lực,
và mọi phép tính tiền nhận một mốc thời gian làm tham số.

Lý do không phải lý thuyết. Công thức bồi thường pin thuê tra giá pin tại
*thời điểm xảy ra sự cố* nhưng tra thời gian bảo hành theo chính sách tại
*thời điểm hình thành tài sản* — hai mốc khác nhau trong cùng một công thức.
Hàm nào chỉ biết "hiện tại" thì không diễn đạt được nghiệp vụ này.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Protocol, TypeVar


class Effective(Protocol):
    """Bản ghi có khoảng hiệu lực. `effective_to = None` nghĩa là còn hiệu lực."""

    effective_from: date
    effective_to: date | None


T = TypeVar("T", bound=Effective)


def is_effective_on(record: Effective, as_of: date) -> bool:
    if as_of < record.effective_from:
        return False
    return record.effective_to is None or as_of < record.effective_to


def effective_on(records: Sequence[T], as_of: date) -> list[T]:
    """Lọc các bản ghi có hiệu lực tại `as_of`."""
    return [r for r in records if is_effective_on(r, as_of)]


def latest_effective_on(records: Sequence[T], as_of: date) -> T | None:
    """Bản ghi có hiệu lực tại `as_of`, ưu tiên bản bắt đầu muộn nhất.

    Trả về None khi không có bản ghi nào phủ mốc thời gian đó — đây là trường
    hợp thật, ví dụ hỏi giá ở một tỉnh chưa có bảng phí. Gọi hàm phải xử lý
    None, không được mặc định về 0.
    """
    candidates = effective_on(records, as_of)
    if not candidates:
        return None
    return max(candidates, key=lambda r: r.effective_from)
