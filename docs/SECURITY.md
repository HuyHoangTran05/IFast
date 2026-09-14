# Bảo mật — tài sản, hiện trạng, và điều kiện trước production

Chủ sở hữu: R4a (hạ tầng và bí mật), R2b (xác thực và dữ liệu khách hàng).

Tài liệu này mô tả **hiện trạng thật**, kể cả phần chưa làm. Một tài liệu bảo mật
mô tả điều mình mong muốn thay vì điều đang có thì nguy hiểm hơn là không có, vì
nó tạo cảm giác an toàn sai.

Liên quan: [ARCHITECTURE.md](ARCHITECTURE.md) · [PRD backend](product/backend-prd.md)
· [quy ước API](product/api-conventions.md).

## 1. Tài sản cần bảo vệ

Xếp theo mức thiệt hại nếu mất.

| # | Tài sản | Ở đâu | Thiệt hại nếu mất |
| --- | --- | --- | --- |
| A1 | Khoá cổng thanh toán | **Chưa có trong repo** | Mất tiền thật, ngay lập tức |
| A2 | Khoá nhà cung cấp LLM | **Chưa có trong repo** | Mất tiền theo lượng dùng, khó phát hiện sớm |
| A3 | PII khách đặt cọc | Sẽ nằm ở `users`, `orders` | Nghĩa vụ pháp lý, mất uy tín |
| A4 | Số tiền và snapshot đơn hàng | `orders_order` | Tranh chấp hợp đồng với khách |
| A5 | Thông tin đăng nhập CSDL production | `IFAST_DATABASE_URL` | Truy cập toàn bộ A3 và A4 |
| A6 | Tính toàn vẹn của bảng giá | `pricing_*` | Bán sai giá; rủi ro pháp lý |

A1 và A2 chưa tồn tại. Đó là điều tốt nhất về tình hình bảo mật hiện tại: **repo
đang public và chưa có gì đáng lấy**. Trạng thái đó sẽ thay đổi khi làm
`payments` hoặc adapter LLM thật.

## 2. Hiện trạng — những gì chưa có

Không tô hồng. Mỗi mục dưới đây là một khoảng trống có thật.

**S-01 — Không có xác thực.** Không endpoint nào kiểm tra danh tính. `POST /orders`
hiện ai gọi cũng được, không giới hạn. Bất kỳ ai biết URL đều tạo được đơn với
mã tuỳ ý, và đọc được đơn của người khác nếu đoán được mã.
*Bằng chứng:* không có middleware hay dependency xác thực nào trong `api/`;
`api/auth/` chỉ có `README.md`.

**S-02 — Mã đơn do client tự đặt.** `CreateOrderIn.code` là chuỗi client gửi lên.
Mã dễ đoán cộng với S-01 nghĩa là đơn của khách khác đọc được.

**S-03 — Không có rate limit.** Không giới hạn số request. Tạo hàng loạt đơn rác
hoặc quét mã đơn đều không bị chặn.

**S-04 — Thông báo lỗi lộ chi tiết nội bộ.** `detail` trả nguyên văn thông báo
của service, kèm `trim_id` và mốc thời gian:
`"không có giá cho trim=7 mô hình=battery_lease tại 2026-09-14"`. Cho phép dò
cấu trúc dữ liệu bên trong.

**S-05 — Không có CORS cấu hình tường minh.** Sẽ phải thêm ở bước 1 của plan P2,
và khi thêm thì **không dùng `*`** một khi đã có xác thực.

**S-06 — Không có log kiểm toán.** Không ghi lại ai tạo đơn nào, từ đâu, lúc nào.
Khi có tranh chấp thì không có gì để đối chiếu ngoài chính bản ghi đơn.

**S-07 — Repo đang public.** Hiện chấp nhận được vì chưa có A1, A2, A5. Không còn
chấp nhận được ngay khi một trong ba xuất hiện.

**S-08 — `IFAST_DATABASE_URL` là biến môi trường trần.** Chưa có cơ chế quản lý
bí mật. Mật khẩu trong `infra/docker-compose.yml` là `ifast_dev_only`, đặt tên để
không ai nhầm là mật khẩu thật.

## 3. Hiện trạng — những gì đã có

Không dài, nhưng có thật và đang chạy.

**S-10 — Quét bí mật trên toàn bộ lịch sử.** Job `secrets` trong
`.github/workflows/ci.yml` chạy gitleaks với `fetch-depth: 0`, tức quét cả lịch
sử chứ không chỉ diff. Chạy trên mọi PR và mọi push vào `main`.

**S-11 — Không có bí mật thật trong repo.** Đã xác nhận bằng gitleaks đang xanh.

**S-12 — Ranh giới sở hữu được cơ chế hoá.** `.github/CODEOWNERS` yêu cầu đúng
người duyệt cho `infra/`, `.github/workflows/`, `contracts/`, `docs/decisions/`.
*Giới hạn:* chỉ có hiệu lực khi bật branch protection với "Require review from
Code Owners" — đây là cấu hình bên ngoài repo, **chưa xác minh được từ trong cây
mã nguồn**.

**S-13 — Đầu vào được kiểm ở tầng kiểu.** Pydantic từ chối sai kiểu bằng 422.
SQLAlchemy dùng truy vấn tham số hoá nên không có bề mặt SQL injection ở các
đường đi hiện có.

**S-14 — Ràng buộc nghiệp vụ chặn giá trị vô lý.** Tiền cọc âm, tiền cọc vượt
tổng đơn, ưu đãi âm, ưu đãi vượt giá xe — đều bị từ chối ở tầng service, không
phải chỉ ở giao diện.

**S-15 — `ai/` từ chối thay vì bịa khi chưa cấu hình.** `UnconfiguredLlm` ném
`NotConfigured`. Im lặng hỏng còn hơn trả lời sai về giá xe.

## 4. Điều kiện bắt buộc trước production

Đánh số để kiểm được từng mục. **Không mục nào được bỏ qua bằng phán đoán cá
nhân.**

| # | Điều kiện | Chặn bởi | Chủ |
| --- | --- | --- | --- |
| P-1 | Thay biểu phí mẫu trong `api/seed.py` bằng biểu phí pháp lý đã đối chiếu | Q-B2 | R2a + sản phẩm |
| P-2 | Có xác thực; `POST /orders` không còn mở cho mọi người | Q-B3, Q5 của PRD web | R2b |
| P-3 | Mã đơn do máy chủ sinh, không đoán được | — | R2b |
| P-4 | Chuyển repo sang private **trước khi** thêm A1 hoặc A2 | — | R4a |
| P-5 | Bí mật production nằm ngoài repo và ngoài biến môi trường trần | — | R4a |
| P-6 | Thông báo lỗi ra ngoài không lộ cấu trúc nội bộ | Q-B7 | R2b + R1 |
| P-7 | CORS khai báo tường minh, không dùng `*` | — | R2b + R4a |
| P-8 | Có rate limit trên endpoint tạo đơn | Q-S1 dưới đây | R4a + R2b |
| P-9 | Log kiểm toán cho mọi thao tác đụng tới tiền | — | R2b |
| P-10 | Chính sách lưu và xoá PII được ghi thành văn bản và thi hành được | Q-B5 | Sản phẩm + pháp lý |
| P-11 | Bật branch protection với Require review from Code Owners | — | R4a |
| P-12 | Migration chạy được trên PostgreSQL, có sao lưu và có diễn tập phục hồi | Plan P1 mục 4 | R4a |

## 5. Câu hỏi cần quyết định

Các mục dưới đây là **chính sách quan sát được từ bên ngoài**, nên cần authority
trong repo trước khi ai đó viết code. Mặc định cấu hình được không phải authority
— đừng tự chọn một con số rồi commit.

| # | Câu hỏi | Ví dụ về điều chưa được phép tự quyết |
| --- | --- | --- |
| Q-S1 | Ngưỡng rate limit: bao nhiêu request, tính theo gì, vượt thì trả gì? | "60 request mỗi phút mỗi IP" là một chính sách, không phải một mặc định |
| Q-S2 | Thời hạn lưu PII và cách xử lý yêu cầu xoá | Gắn với Q-B5 |
| Q-S3 | Có cần mã lỗi máy đọc được thay cho `detail` tiếng Việt? | Gắn với Q-B7 |
| Q-S4 | Phạm vi và định dạng log kiểm toán — log gì, giữ bao lâu, ai đọc được | Log chứa PII là tài sản A3 chứ không phải dữ liệu vận hành thường |
| Q-S5 | Nhà cung cấp quản lý bí mật cho production | Ảnh hưởng P-5 và toàn bộ quy trình deploy |

## 6. Luật áp dụng ngay, không cần chờ quyết định

- Không đưa bí mật, `.env`, thông tin đăng nhập hay PII vào code, log, commit,
  hay bất kỳ request đi ra ngoài nào.
- Mật khẩu trong `infra/docker-compose.yml` chỉ dành cho máy local. Không tái sử
  dụng ở bất kỳ môi trường nào khác.
- Gitleaks đỏ là một điểm dừng thật. Xoay khoá trước, rồi mới dọn lịch sử — xoá
  khỏi lịch sử không thu hồi được một khoá đã lộ.
- Thêm endpoint mới thì trả lời trước: endpoint này lộ tài sản nào ở mục 1, và ai
  được phép gọi nó.
