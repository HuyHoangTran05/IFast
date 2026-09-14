# P1 — Nền tảng bán xe: luồng tiền đi vào

Status: In progress
Owner: cả 6 vai
Started: 2026-09-14

## Mục tiêu

Dựng lát cắt dọc chạy được của luồng sinh tiền: tìm xe → xem thông số → dự
toán chi phí lăn bánh theo tỉnh → áp ưu đãi → đặt cọc có snapshot. Kèm domain
pin vì đó là quy tắc nghiệp vụ khó nhất và đã có đặc tả thật.

Không nằm trong P1: xe máy điện, phụ kiện, hậu mãi, lưu trữ năng lượng, CMS.

## Giả định đã chốt (do stack chưa được chỉ định)

- Backend: FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, pytest.
- CSDL: PostgreSQL khi chạy thật; SQLite khi chạy test để test không cần Docker.
- Web: Next.js App Router, TypeScript.
- Tiền: **số nguyên đồng**, không dùng float. Tỉ lệ tính bằng `Decimal`.
- Contract: sinh từ backend rồi commit, CI chặn nếu lệch. Xem `contracts/README.md`.
- Môi trường: **bắt buộc dùng `.venv` trong thư mục dự án**. Không cài dependency
  vào Python hệ thống. Lý do cụ thể ở mục Quyết định bên dưới.

Đổi bất kỳ giả định nào ở trên thì sửa tài liệu này trước khi sửa code.

## Bất biến phải giữ

1. Mọi bảng chính sách và bảng giá có **ngày hiệu lực**; mọi hàm tính tiền nhận
   một mốc thời gian làm tham số. Không có hàm nào chỉ đọc "giá hiện tại".
2. Đơn đã chốt giữ **snapshot** giá và ưu đãi; bảng giá đổi sau không làm đổi đơn.
3. `ai/` không tự tính tiền và không tự nhớ thông số — luôn gọi `api/`.
4. Tiền là số nguyên đồng; làm tròn chỉ ở bước cuối, theo luật ghi rõ trong code.

## Tiến độ

- [x] Khung domain và ranh giới sở hữu (decision 0001)
- [x] `api/core` — cấu hình, phiên CSDL, tiện ích chính sách theo thời gian
- [x] `api/catalog` — dòng xe, phiên bản, màu, thông số có kiểu
- [x] `api/pricing` — bảng giá theo thời gian, kèm pin/thuê pin, phí lăn bánh
      theo tỉnh, so sánh chi phí với xe xăng dầu
- [x] `api/promotions` — ưu đãi có hiệu lực theo thời gian, luật ưu tiên
- [x] `api/battery` — tài sản pin, chính sách bảo hành theo thời gian, công thức
      bồi thường
- [x] `api/orders` — đặt cọc có snapshot
- [x] Test cho toàn bộ quy tắc nghiệp vụ khó
- [x] `contracts/openapi.yaml` sinh từ backend
- [x] `infra/` docker-compose và CI
- [x] `web/` — trang danh mục và trang chi tiết xe, gọi API qua client sinh type
      từ contract. Build và typecheck xanh; **chưa chạy web + API cùng lúc**.
- [x] `ai/` — cổng ra LLM, tầng công cụ, và eval cho bốn luật của R3
- [ ] `ai/` — chưa có adapter nhà cung cấp thật (chưa có khoá API) và chưa có RAG
- [ ] `web/` — chưa có trang đặt cọc, chưa có chọn tỉnh, chưa có so sánh chi phí
- [ ] `tests/e2e/` — chưa có; cần web và API chạy cùng lúc trong CI trước
- [ ] Thay dữ liệu biểu phí mẫu bằng biểu phí pháp lý đã đối chiếu

## Quyết định trong lúc làm

- **Contract sinh từ code, không viết tay.** Viết tay OpenAPI cho 12 domain sẽ
  lệch khỏi code trong một tuần. Thay vào đó CI chạy lại generator và fail nếu
  `contracts/openapi.yaml` khác bản sinh ra. Luật với R1 không đổi: không viết
  tay type, và đổi contract vẫn là PR riêng.
- **Tiền dùng số nguyên đồng.** VND không có phần thập phân; dùng float cho
  tiền là lỗi kinh điển.
- **Bắt buộc dùng virtualenv.** Lần dựng đầu tiên đã cài dependency vào Python
  hệ thống và dính đúng cái bẫy mà venv sinh ra để ngăn: trên máy Windows này
  `python` trỏ vào Anaconda còn `pip` trỏ vào bản Python từ Microsoft Store,
  nên `pip install ruff` cài vào một interpreter trong khi `python -m ruff`
  chạy interpreter khác — mất một vòng CI mới phát hiện. Việc đó còn nâng
  `ruff` global của máy từ 0.12.0 lên 0.16.7, tức là sửa máy cá nhân để hợp ý
  một dự án. Từ nay mọi lệnh Python chạy trong `.venv` của repo.

## Phục hồi

Nếu phải dừng giữa chừng: `api/` chạy độc lập được bằng `pytest`, không cần web
và không cần Docker. Bắt đầu lại từ mục chưa tick ở trên.
