# Execution Plan: P1 — Nền tảng bán xe, luồng tiền đi vào

Date: 2026-09-14

## Status

Active

## Outcome

Khách vào web, tìm được xe, xem đúng thông số, biết chi phí lăn bánh tại tỉnh
của mình, thấy ưu đãi đang áp dụng, và đặt cọc được — với mọi con số tiền đều
tra được nguồn và không đổi sau khi đơn đã chốt.

Hiện đạt được ở mức API. Web mới có trang danh mục và trang chi tiết xe.

## Context

- Phân vai và ranh giới sở hữu: `docs/decisions/0001-team-roles-and-ownership-boundaries.md`
- Cách chạy và kiểm chứng: `docs/RUNBOOK.md`
- Contract giữa backend và web: `contracts/openapi.yaml`, sinh bằng `scripts/generate-contract.py`
- Quy ước chung cho agent: `AGENTS.md`

Domain được đối chiếu với vinfastauto.com (trang chủ, trang đặt cọc VF 2, trang
dịch vụ pin) thay vì suy đoán.

## Scope

In scope:

- Danh mục xe với thông số có kiểu dữ liệu.
- Bảng giá theo thời gian, hai mô hình sở hữu: kèm pin và thuê pin.
- Dự toán chi phí lăn bánh theo tỉnh.
- So sánh chi phí vận hành với xe xăng dầu.
- Ưu đãi có vòng đời và luật ưu tiên.
- Pin thuê: tài sản, chính sách bảo hành, công thức bồi thường.
- Đặt cọc có snapshot.

Out of scope (giai đoạn sau, chưa phân vai):

- Xe máy điện, phụ kiện, thương mại điện tử.
- Dịch vụ hậu mãi và đặt lịch bảo dưỡng.
- Lưu trữ năng lượng.
- Tin tức, CMS, trang chính sách.
- Bản đồ showroom và trạm sạc.

## Approach

Làm backend trước và làm cho đúng, vì toàn bộ rủi ro nghiệp vụ nằm ở đó: sai
một con số tiền trên trang bán xe là rủi ro pháp lý. Web bám theo contract sinh
từ backend nên không phải chờ.

Bốn bất biến được cơ chế hoá bằng code chứ không chỉ viết trong tài liệu:

1. Mọi bảng chính sách có ngày hiệu lực; mọi hàm tính tiền nhận `as_of`.
   Nơi duy nhất tra cứu theo thời điểm: `api/core/effective.py`.
2. Tiền là số nguyên đồng, không dùng float. `api/core/money.py`.
3. Đơn đã chốt giữ snapshot, không đọc lại bảng giá. `api/orders/`.
4. `ai/` không tự tính tiền và không tự nhớ thông số; mọi con số đi qua `api/`
   và mang theo nguồn. `ai/tools.py`, có eval quét mã nguồn để chặn.

## Risks And Recovery

- **Dữ liệu biểu phí là dữ liệu mẫu.** Biểu phí lăn bánh, giá điện, giá nhiên
  liệu trong `api/seed.py` chưa đối chiếu pháp lý. Rủi ro: ai đó tưởng là số
  thật rồi đưa lên production. Giảm thiểu: đã ghi cảnh báo trong chính file,
  trong `README.md` và trong `docs/RUNBOOK.md`. **Phải thay trước khi lên
  production.**
- **Repo đang public.** Chưa có khoá thanh toán hay khoá nhà cung cấp AI trong
  repo, và CI đã có bước quét bí mật. Nhưng nên chuyển private trước khi thêm.
- **Web chưa từng chạy cùng API.** Rủi ro: contract đúng trên giấy nhưng sai
  khi chạy thật. Giảm thiểu: đây là việc đầu tiên trong danh sách tiếp theo.
- **Phục hồi:** không có trạng thái nào nằm ngoài thư mục dự án.
  `rm -f ifast.db && python scripts/seed-dev.py` đưa về trạng thái sạch.
  `api/` chạy và test được độc lập, không cần web và không cần Docker.

## Progress

Đã xong và đã kiểm chứng:

- [x] Khung domain và ranh giới sở hữu (decision 0001, CODEOWNERS, 6 agent)
- [x] `api/core` — tiền, tra cứu theo thời điểm, ngày nghiệp vụ theo giờ VN
- [x] `api/catalog` — dòng xe, phiên bản, màu, thông số có kiểu
- [x] `api/pricing` — bảng giá theo thời gian, kèm pin và thuê pin, phí lăn
      bánh theo tỉnh, so sánh chi phí với xe xăng dầu
- [x] `api/promotions` — ưu đãi có hiệu lực theo thời gian, luật ưu tiên tất định
- [x] `api/battery` — tài sản pin, chính sách bảo hành theo thời gian, công
      thức bồi thường có sàn 10%
- [x] `api/orders` — đặt cọc có snapshot, hai luồng mua
- [x] 60 test cho toàn bộ quy tắc nghiệp vụ khó
- [x] `contracts/openapi.yaml` sinh từ backend, CI chặn khi lệch
- [x] Alembic, migration đầu tiên chạy được cả upgrade lẫn downgrade (SQLite)
- [x] `infra/` docker-compose và CI GitHub Actions, cả hai job xanh
- [x] `ai/` — cổng ra LLM, tầng công cụ, 7 eval cho bốn luật của R3
- [x] `web/` — trang danh mục và trang chi tiết xe, type sinh từ contract

Chưa xong, **theo đúng thứ tự nên làm**:

- [ ] **1. Chạy web và API cùng lúc.** Việc đầu tiên của người tiếp quản. Mọi
      thứ khác đều giả định bước này đã đúng. Xem `docs/RUNBOOK.md`. Đã chuyển sang
      [plan P2](p2-trai-nghiem-ban-xe-tren-web.md) bước 1.
- [ ] **2. Trang chọn tỉnh và trang đặt cọc trong `web/`.** Đã chuyển sang
      [plan P2](p2-trai-nghiem-ban-xe-tren-web.md). (R1)
- [ ] **3. `tests/e2e/` cho luồng đặt cọc.** Cần bước 1 và 2 trước. Đã chuyển
      sang [plan P2](p2-trai-nghiem-ban-xe-tren-web.md) bước 7. (R4b)
- [ ] **4. Chạy `docker compose up` thật và migrate trên PostgreSQL.** Hiện mới
      kiểm chứng trên SQLite. (R4a)
- [ ] **5. Thay dữ liệu biểu phí mẫu bằng biểu phí pháp lý đã đối chiếu.** (R2a)
- [ ] **6. Adapter nhà cung cấp mô hình thật cho `ai/`.** Cần khoá API và trần
      chi phí trước. (R3 và R4a)
- [ ] **7. Thanh toán thật và thuê bao thuê pin.** Ranh giới tiền bạc, cần một
      decision doc trước khi viết code. (R2b)

## Decisions

- 2026-09-14: **Stack chọn theo mặc định hợp lý** vì chưa được chỉ định:
  FastAPI + SQLAlchemy 2 + Alembic + PostgreSQL, Next.js + TypeScript, pytest.
  Đổi bất kỳ giả định nào thì sửa tài liệu này trước khi sửa code.
- 2026-09-14: **Tiền là số nguyên đồng.** VND không có phần thập phân; dùng
  float cho tiền là lỗi kinh điển và sai số tích luỹ qua các phép nhân phần trăm.
- 2026-09-14: **Contract sinh từ code, không viết tay.** Viết tay OpenAPI cho
  hàng chục domain sẽ lệch khỏi code trong một tuần, và khi đó R1 code theo một
  tài liệu sai — tệ hơn là không có tài liệu. Đổi lại, CI chạy `--check` nên
  mọi thay đổi contract đều lộ ra thành diff và không lọt âm thầm vào PR feature.
- 2026-09-14: **Bắt buộc dùng `.venv`.** Lần dựng đầu tiên cài dependency vào
  Python hệ thống và dính đúng cái bẫy mà venv sinh ra để ngăn: trên máy
  Windows này `python` trỏ vào Anaconda còn `pip` trỏ vào bản từ Microsoft
  Store, nên gói cài ở một interpreter còn lệnh chạy ở interpreter khác — mất
  một vòng CI mới phát hiện.
- 2026-09-14: **Ghim phiên bản ruff và khai báo rule tường minh.** Linter thả
  lỏng khiến CI đỏ khi bên thứ ba phát hành bản mới, dù không ai sửa dòng code
  nào. Đã xảy ra một lần.
- 2026-09-14: **Ngày nghiệp vụ theo giờ Việt Nam**, không theo giờ máy chủ.
  Máy chủ chạy UTC thì ưu đãi bắt đầu ngày 10/02 chỉ có hiệu lực từ 7 giờ sáng
  giờ Việt Nam, và đơn đặt lúc 23 giờ bị ghi sang ngày hôm trước.
  `api/core/clock.py`.

## Validation

- Focused proof: `python -m pytest` — 60 test (53 api, 7 eval ai).
- Integration proof: chạy uvicorn thật rồi gọi API. Đã xác nhận HN
  202.980.700 khác HCM 193.980.700 cùng ngày; cùng HN thì 2026 lệ phí trước bạ
  0 còn 2027 là 10.716.000; bồi thường pin sau 24 tháng 67.500.000 và sau 94
  tháng chạm sàn 9.000.000; sau khi tăng giá lên 220 triệu thì báo giá mới ra
  234.980.700 còn đơn đã chốt vẫn giữ 202.980.700.
- End-to-end proof: **chưa có.** Web chưa từng chạy cùng API.
- Repository-required checks: `python scripts/generate-contract.py --check`,
  `ruff check`, `ruff format --check`, và `cd web && npm run typecheck && npm run build`.
  Toàn bộ nằm trong `.github/workflows/ci.yml`, hiện xanh.

## Result

Chưa hoàn tất. Hoàn tất khi luồng đặt cọc chạy được đầu-cuối trên web với E2E
test xanh, và dữ liệu biểu phí đã được thay bằng số liệu pháp lý.
