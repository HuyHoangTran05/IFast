# 0001 Phân vai và ranh giới sở hữu cho 6 người

Date: 2026-09-14

## Status

Accepted

## Context

IFast là sản phẩm web bán ô tô điện, có tính năng AI, do 6 người phát triển
trên một repo chung. Yêu cầu đặt ra là chia vai sao cho ít conflict.

Conflict trong git không sinh ra từ người, nó sinh ra từ **file mà nhiều người
cùng sửa**. Vì vậy bài toán phân vai thực chất là bài toán chia quyền sở hữu
thư mục sao cho không giao nhau, cộng với việc xử lý riêng một nhúm file mà ai
cũng có lý do chạm vào.

Ràng buộc do người dùng đặt: R1 một người, R2 hai người, R3 một người, R4 hai
người.

Phạm vi nghiệp vụ được đối chiếu với vinfastauto.com (trang chủ, trang đặt cọc
VF 2, trang dịch vụ pin) để ranh giới domain bám vào nghiệp vụ thật thay vì
suy đoán.

## Decision

Sáu vai, mỗi vai sở hữu một tập thư mục không giao nhau:

| Vai | Người | Sở hữu |
|---|---|---|
| R1 Frontend | @angWindy | `web/` |
| R2a Sản phẩm & giá | @HuyHoangTran05 | `api/catalog` `pricing` `promotions` `inventory` `battery` `dealers` |
| R2b Khách hàng & giao dịch | @qkhanhbe | `api/orders` `payments` `testdrive` `users` `auth` `notifications`, `contracts/` |
| R3 AI | @trunghieunef | `ai/` |
| R4a Platform/DevOps | @lam3082004 | `infra/`, `.github/workflows/`, `repository-harness/` |
| R4b Quality/Release | @hieu7404 | `tests/` |

Ánh xạ người vào vai là gán ban đầu, sửa ở đầu `.github/CODEOWNERS`.

Backend chia theo **domain dọc** ("bán cái gì" và "ai mua, mua thế nào"), không
chia theo tầng. Chia theo tầng khiến mọi feature cần cả hai người sửa.

Ranh giới được cơ chế hoá bằng `.github/CODEOWNERS` và sáu định nghĩa agent
trong `.claude/agents/`, mỗi agent ghi rõ vùng được sửa và vùng cấm.

### Bốn đường may và luật đi kèm

1. **`contracts/openapi.yaml` (R2b ↔ R1)** — nguồn sự thật duy nhất của API.
   R1 generate type và code song song, không chờ backend. Đổi contract là PR
   riêng dán nhãn `contract`, cần R1 approve, không trộn vào PR feature.
2. **Snapshot đơn hàng (R2a ↔ R2b)** — `orders/` chụp giá và ưu đãi vào đơn lúc
   chốt, sau đó không đọc lại `pricing/`. Vừa đúng nghiệp vụ, vừa cắt phụ thuộc.
3. **`ai/` chỉ nói chuyện với `api/` (R3 ↔ mọi người)** — không lộ trực tiếp ra
   client, nên R3 đổi prompt/model không đụng file của ai.
4. **CI (R4a ↔ R4b)** — R4a sở hữu `.github/workflows/`, R4b mở PR khi cần thêm
   bước test.

### Luật cho file dùng chung

- Entrypoint, config, `.env.example` của `api/`: R2b sở hữu, **append-only**.
- Migration: conflict thì **xoá migration của mình, pull, generate lại**. Không
  sửa tay `down_revision`.
- `contracts/generated/**`: output của script, conflict thì chạy lại generator.
- Số hiệu decision: đánh theo **số PR**, không dùng chuỗi tăng dần 0001, 0002 —
  hai người cùng lấy một số là conflict chắc chắn. Tài liệu này mang số 0001 vì
  được tạo trước khi luật có hiệu lực.
- `docs/plans/active/`: một file một plan, không hai người cùng sửa một file.

### Một bất biến xuyên suốt domain

Khảo sát trang thật cho thấy gần như mọi con số đều gắn với một mốc thời gian:
giá niêm yết và giá ưu đãi, ưu đãi miễn phí sạc có ngày bắt đầu, giá nhiên liệu
tham chiếu cập nhật theo ngày, giá pin công bố, và thời gian bảo hành áp dụng
theo chính sách tại thời điểm hình thành tài sản.

Do đó: **mọi bảng chính sách và bảng giá đều có ngày hiệu lực, và mọi phép tính
tiền đều nhận một mốc thời gian làm tham số.** Không viết hàm tính tiền chỉ đọc
"giá hiện tại".

Ví dụ cụ thể nhất là công thức bồi thường pin thuê `B = A × (1 − T1/T2)`, trong
đó `A` tra tại thời điểm xảy ra sự cố còn `T2` tra tại thời điểm hình thành tài
sản — hai mốc khác nhau trong cùng một công thức, cộng luật làm tròn 15 ngày và
sàn 10%.

## Alternatives Considered

1. **Chia theo tầng** (một người model, một người API). Bị loại: mọi feature
   cần cả hai người sửa, conflict ở mọi PR.
2. **Chia theo lát cắt dọc full-stack** (mỗi người một feature từ UI xuống DB).
   Tốc độ tốt hơn nhưng hai người cùng sửa `web/` và `api/` một lúc — ngược
   với mục tiêu giảm conflict.
3. **Bốn vai cho bốn người**, gồm cả vai Mobile. Bị loại sau khi xác nhận sản
   phẩm chỉ làm web.

## Consequences

Positive:

- Mỗi file có đúng một chủ, nên phần lớn PR không bao giờ chạm nhau.
- GitHub tự gán reviewer đúng người, không phụ thuộc trí nhớ.
- Agent trong `.claude/agents/` mang sẵn luật ranh giới, nên khi dùng Claude
  Code thì luật được áp ngay lúc code chứ không đợi tới lúc review.

Tradeoffs:

- **R1 là nút thắt.** Frontend một người trong khi backend hai và platform hai.
  Đây là nút thắt tiến độ, không phải nút thắt conflict. Giảm tải bằng cách
  đẩy E2E sang R4b, và giai đoạn sau cho R4a mượn theo **route** chứ không bao
  giờ cho mượn `web/src/components/ui/**`.
- Contract-first thêm một PR cho mỗi lần đổi API. Đổi lại là frontend không
  phải chờ backend.
- Ranh giới cứng khiến vài việc phải đi qua hai người (ví dụ R2a cần biến môi
  trường mới). Chấp nhận, vì rẻ hơn conflict.

## Follow-Up

- Bật branch protection trên `main` với "Require review from Code Owners" —
  không có bước này thì `CODEOWNERS` chỉ là tài liệu.
- Ba collaborator đang ở trạng thái Pending Invite. GitHub **bỏ qua** dòng
  CODEOWNERS trỏ tới người chưa nhận lời mời, nên phải nhận lời mời xong bảng
  này mới có hiệu lực thật.
- Chốt stack cụ thể rồi bổ sung tên lockfile vào luật file dùng chung.
- Cân nhắc chuyển repo sang private trước khi có khoá thanh toán hay khoá nhà
  cung cấp AI.
- Phạm vi giai đoạn sau chưa phân vai: xe máy điện, phụ kiện, dịch vụ hậu mãi
  và đặt lịch bảo dưỡng, lưu trữ năng lượng, tin tức/CMS.
