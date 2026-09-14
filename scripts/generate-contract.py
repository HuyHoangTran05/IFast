#!/usr/bin/env python
"""Sinh contracts/openapi.yaml từ backend.

Quyết định: contract **sinh từ code**, không viết tay. Viết tay OpenAPI cho
hàng chục domain sẽ lệch khỏi code trong vòng một tuần, và lúc đó R1 code theo
một tài liệu sai — tệ hơn là không có tài liệu.

Luật với R1 không đổi: không viết tay type, sinh từ file này. Đổi contract vẫn
là PR riêng, vì CI sẽ bắt mọi thay đổi của file này lộ ra thành diff.

Dùng:
    python scripts/generate-contract.py           # ghi file
    python scripts/generate-contract.py --check   # chỉ kiểm tra, dùng trong CI
"""

from __future__ import annotations

import pathlib
import sys

import yaml

# Console Windows mac dinh la cp1252, khong in duoc tieng Viet co dau va se ném
# UnicodeEncodeError. Team dung Windows nen ep UTF-8 ngay tu dau thay vi bo dau.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from api.main import app  # noqa: E402

TARGET = pathlib.Path(__file__).resolve().parents[1] / "contracts" / "openapi.yaml"


def render() -> str:
    return yaml.safe_dump(app.openapi(), sort_keys=True, allow_unicode=True, width=100)


def main() -> int:
    rendered = render()
    if "--check" in sys.argv:
        if not TARGET.exists():
            print(f"thiếu {TARGET}", file=sys.stderr)
            return 1
        current = TARGET.read_text(encoding="utf-8")
        if current != rendered:
            print(
                "contracts/openapi.yaml đã lệch khỏi backend.\n"
                "Chạy: python scripts/generate-contract.py",
                file=sys.stderr,
            )
            return 1
        print("contract khớp backend")
        return 0

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(rendered, encoding="utf-8")
    print(f"đã ghi {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
