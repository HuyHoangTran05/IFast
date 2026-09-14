"""Cổng ra mô hình ngôn ngữ.

`ai/` không khoá cứng vào một nhà cung cấp. Đổi model hay đổi provider là việc
thường xuyên của R3, và nó không được phép lan sang `api/` hay `web/`.

Chưa có adapter thật vì chưa có khoá API. Khi có, hiện thực `LlmPort` rồi tiêm
vào — không sửa chỗ gọi.
"""

from __future__ import annotations

from typing import Protocol


class LlmPort(Protocol):
    def complete(self, *, system: str, prompt: str) -> str: ...


class NotConfigured(Exception):
    """Chưa cấu hình nhà cung cấp mô hình."""


class UnconfiguredLlm:
    """Adapter mặc định: từ chối thay vì bịa.

    Trả lời sai về giá xe là rủi ro pháp lý, nên khi chưa cấu hình thì im lặng
    hỏng còn hơn trả lời bừa.
    """

    def complete(self, *, system: str, prompt: str) -> str:
        raise NotConfigured("chưa cấu hình nhà cung cấp mô hình cho ai/")
