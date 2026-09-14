# IFast

Nền tảng web bán ô tô điện.

> **Mới tiếp quản dự án?** Đọc [`docs/HANDOFF.md`](docs/HANDOFF.md) trước.
> Nó nói bạn cần chạy gì trước, việc tiếp theo là gì, và những cái bẫy đã biết.
> Cách chạy chi tiết ở [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

## Chạy nhanh

**Luôn làm việc trong virtualenv.** Không cài dependency của dự án vào Python
hệ thống — trên Windows rất dễ rơi vào cảnh `python` trỏ vào một interpreter
còn `pip` trỏ vào interpreter khác, và lúc đó bạn cài một nơi rồi chạy một nơi.
Venv cũng giữ cho `ruff` của dự án đúng phiên bản đã ghim mà không đụng vào
`ruff` bạn dùng cho việc khác.

```bash
# Backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS / Linux

pip install -e ".[dev]"
python scripts/seed-dev.py
uvicorn api.main:app --reload            # http://localhost:8000/docs

# Web
cd web && npm install && npm run dev     # http://localhost:3000

# Cả stack bằng PostgreSQL
docker compose -f infra/docker-compose.yml up --build
```

## Kiểm chứng

Chạy trong venv đã kích hoạt:

```bash
python -m pytest                          # 60 test
python scripts/generate-contract.py --check
python -m ruff check api ai alembic scripts
cd web && npm run typecheck && npm run build
```

## Bốn bất biến của hệ thống

Vi phạm bất kỳ điều nào dưới đây là lỗi nghiêm trọng, không phải lựa chọn phong cách.

1. **Mọi phép tính tiền nhận một mốc thời gian.** Bảng giá, biểu phí, ưu đãi,
   chính sách bảo hành đều có ngày hiệu lực. Không viết hàm chỉ đọc "giá hiện tại".
   Xem `api/core/effective.py`.
2. **Tiền là số nguyên đồng.** Không dùng float cho tiền. Xem `api/core/money.py`.
3. **Đơn đã chốt giữ snapshot.** Bảng giá đổi sau không làm đổi đơn đã ký.
   Xem `api/orders/models.py`.
4. **`ai/` không tự tính tiền và không tự nhớ thông số.** Mọi con số đi qua
   `api/` và mang theo nguồn. Xem `ai/tools.py`.

## Bản đồ thư mục và chủ sở hữu

| Thư mục | Chủ | Nội dung |
|---|---|---|
| `web/` | R1 | Web client (Next.js) |
| `api/catalog` `pricing` `promotions` `inventory` `battery` `dealers` | R2a | Sản phẩm và giá |
| `api/orders` `payments` `testdrive` `users` `auth` `notifications`, `contracts/` | R2b | Khách hàng và giao dịch |
| `ai/` | R3 | Tư vấn, so sánh, chatbot, eval |
| `infra/`, `.github/workflows/` | R4a | Hạ tầng, CI/CD |
| `tests/` | R4b | E2E, release, security |

Ranh giới và luật chống conflict: `docs/decisions/0001-team-roles-and-ownership-boundaries.md`.
Tiến độ hiện tại: `docs/plans/active/p1-nen-tang-ban-xe.md`.

## Lưu ý trước khi lên production

- Biểu phí lăn bánh, giá điện và giá nhiên liệu trong `api/seed.py` là **dữ liệu
  mẫu chưa đối chiếu pháp lý**. Phải thay bằng biểu phí chính thức.
- Repo đang public. Cân nhắc chuyển private trước khi thêm khoá thanh toán hay
  khoá nhà cung cấp AI.

## Quy ước làm việc

Đọc `AGENTS.md`. Mỗi file có đúng một chủ (`.github/CODEOWNERS`). Agent theo vai
nằm trong `.claude/agents/`.
