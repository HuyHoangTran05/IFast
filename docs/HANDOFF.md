# Bàn giao — đọc file này trước

Tài liệu này dành cho người tiếp quản IFast. Mục tiêu: trong 15 phút bạn chạy
được hệ thống, biết nó đang ở đâu, và biết việc tiếp theo là gì.

Cập nhật lần cuối: 2026-09-14.

## Dự án này là gì

IFast là nền tảng web bán ô tô điện. Mô hình nghiệp vụ tham chiếu VinFast: bán
xe kèm pin hoặc cho thuê pin, đặt cọc trực tuyến, dự toán chi phí lăn bánh
theo tỉnh, và có trợ lý AI tư vấn.

Hiện có: **backend hoàn chỉnh cho luồng tiền đi vào**, web mới có hai trang, AI
mới có tầng công cụ chưa nối mô hình thật.

## Chạy gì trước

Theo đúng thứ tự này. Chi tiết đầy đủ ở `docs/RUNBOOK.md`.

```bash
# 1. Môi trường — BẮT BUỘC dùng venv, đọc mục Bẫy bên dưới để biết vì sao
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -e ".[dev]"

# 2. Chứng minh mọi thứ còn xanh trước khi sửa bất cứ gì
python -m pytest                          # phải ra 60 passed
python scripts/generate-contract.py --check

# 3. Chạy API
python scripts/seed-dev.py
uvicorn api.main:app --reload             # http://localhost:8000/docs

# 4. Xem nghiệp vụ hoạt động
curl -s "http://localhost:8000/pricing/on-road?trim_id=1&province_code=HN&as_of=2026-06-01"
curl -s "http://localhost:8000/pricing/on-road?trim_id=1&province_code=HCM&as_of=2026-06-01"
# Hai lệnh trên phải ra hai con số khác nhau. Nếu giống nhau là có gì đó hỏng.
```

Nếu `pytest` không ra 60 passed thì **dừng lại và tìm nguyên nhân trước khi
viết code mới**. Đó là đường cơ sở duy nhất bạn có.

## Việc tiếp theo, theo thứ tự

Danh sách đầy đủ kèm chủ sở hữu nằm ở `docs/plans/active/p1-nen-tang-ban-xe.md`.

1. **Chạy web và API cùng lúc.** Web đã build và typecheck xanh, nhưng chưa có
   lần nào trang thật gọi API thật. Mọi việc còn lại đều giả định bước này
   đúng. Làm việc này đầu tiên.
2. **Trang chọn tỉnh và trang đặt cọc trong `web/`.** API đã sẵn sàng.
3. **`tests/e2e/` cho luồng đặt cọc.** Cần bước 1 và 2.
4. **Chạy `docker compose up` thật và migrate trên PostgreSQL.** Hiện mới chạy
   trên SQLite.
5. **Thay dữ liệu biểu phí mẫu bằng số liệu pháp lý.**

## Bốn bất biến, đừng phá

Vi phạm là lỗi nghiêm trọng, không phải lựa chọn phong cách. Mỗi cái đều có
test canh.

1. **Mọi phép tính tiền nhận một mốc thời gian.** Không viết hàm chỉ đọc "giá
   hiện tại". `api/core/effective.py`.
2. **Tiền là số nguyên đồng.** Không dùng float cho tiền. `api/core/money.py`.
3. **Đơn đã chốt giữ snapshot.** Bảng giá đổi sau không làm đổi đơn đã ký.
   `api/orders/models.py`.
4. **`ai/` không tự tính tiền và không tự nhớ thông số.** `ai/tools.py`.

Lý do bất biến 1 không phải lý thuyết: công thức bồi thường pin thuê tra giá
pin tại *thời điểm xảy ra sự cố* nhưng tra thời gian bảo hành theo chính sách
tại *thời điểm hình thành tài sản* — hai mốc khác nhau trong cùng một phép
tính. Xem `api/battery/service.py`.

## Bẫy đã biết

Mỗi mục dưới đây đã thực sự làm mất thời gian trong phiên dựng đầu tiên. Đọc
để không mất lần nữa.

**`python` và `pip` có thể là hai interpreter khác nhau.** Trên máy Windows đã
dùng, `python` trỏ vào Anaconda còn `pip` trỏ vào bản Python từ Microsoft
Store. `pip install X` cài vào một nơi còn `python -m X` chạy ở nơi khác, nên
bạn tưởng đã cài xong mà phiên bản không đổi. Luôn dùng `.venv` và luôn gọi
`python -m pip`, không gọi `pip` trần.

**`pytest` xanh không có nghĩa là CI sẽ xanh.** CI chạy `pip install -e .`, đi
qua build backend, còn `pytest` thì không. Lần đầu CI đỏ vì setuptools thấy
`api`, `ai`, `web`, `infra` cùng cấp và từ chối đoán package nào cần đóng gói.
Muốn chắc thì chạy đúng lệnh CI chạy.

**Console Windows là cp1252 và sẽ ném `UnicodeEncodeError` khi in tiếng Việt.**
Script trong `scripts/` đã tự ép UTF-8. Script bạn tự viết thì đặt
`PYTHONIOENCODING=utf-8`.

**Harness hash byte thô.** `.gitattributes` đánh dấu `AGENTS.md`, `CLAUDE.md`,
`docs/**`, `.agents/**`, `.harness-core/**` là `-text` để git không đổi line
ending. **Đừng bỏ dòng đó.** Bỏ đi thì mọi người clone repo sẽ thấy
`harness status` chết với `base hash mismatch`.

**Linter không ghim phiên bản sẽ làm đỏ CI khi bên thứ ba ra bản mới.** `ruff`
đã được ghim đúng phiên bản trong `pyproject.toml` và tập rule cũng khai báo
tường minh. Đổi phiên bản thì phải chạy lại `ruff check` toàn repo trước khi push.

**`harness status` báo `modified` khác 0 là bình thường.** Harness quản lý
`docs/README.md` và `docs/decisions/README.md`, cả hai đã được sửa có chủ ý để
thêm mục lục. Harness hỗ trợ sửa đổi phía người dùng và merge ba chiều khi cập
nhật. Chạy `harness doctor` để xem chính xác file nào lệch.

## Đừng tin gì trong này

**Biểu phí lăn bánh, giá điện, giá nhiên liệu trong `api/seed.py` là dữ liệu
mẫu chưa đối chiếu pháp lý.** Chúng đủ để hệ thống chạy và để test, nhưng
không phải số liệu thật. Phải thay trước khi lên production.

Thông số xe VF 2 và giá 178.600.000 / 188.000.000 lấy từ trang công khai của
VinFast tại thời điểm khảo sát, dùng làm dữ liệu mẫu.

## Chưa từng chạy thật

Đừng viết tài liệu cho những thứ này như thể chúng hoạt động:

- `docker compose up` — mới xác nhận cú pháp, chưa chạy.
- Alembic trên PostgreSQL — mới chạy trên SQLite.
- Web gọi API thật.
- `ai/` gọi nhà cung cấp mô hình — chưa có khoá, chưa có adapter thật.

## Ai sở hữu cái gì

| Vùng | Vai |
|---|---|
| `web/` | R1 Frontend |
| `api/catalog` `pricing` `promotions` `inventory` `battery` `dealers` | R2a Sản phẩm và giá |
| `api/orders` `payments` `testdrive` `users` `auth` `notifications`, `contracts/` | R2b Khách hàng và giao dịch |
| `ai/` | R3 AI |
| `infra/`, `.github/workflows/` | R4a Platform |
| `tests/` | R4b Quality |

Mỗi file có đúng một chủ, xem `.github/CODEOWNERS`. Luật chống conflict và lý
do đằng sau: `docs/decisions/0001-team-roles-and-ownership-boundaries.md`.

Dùng Claude Code thì có sẵn 6 agent theo vai trong `.claude/agents/`, mỗi agent
đã mang sẵn vùng được sửa và vùng cấm.

## Việc cần con người quyết, chưa ai làm

- **Bật branch protection** trên `main` với *Require review from Code Owners*.
  Không có bước này thì `CODEOWNERS` chỉ là tài liệu, không chặn được gì.
- **Ba collaborator còn ở trạng thái Pending Invite.** GitHub bỏ qua dòng
  CODEOWNERS trỏ tới người chưa nhận lời mời.
- **Ánh xạ người vào vai là gán ban đầu**, sửa ở khối đầu `.github/CODEOWNERS`.
- **Repo đang public.** Cân nhắc chuyển private trước khi thêm khoá thanh toán
  hoặc khoá nhà cung cấp AI.
- **Stack chưa được chỉ định chính thức.** Lựa chọn hiện tại là mặc định hợp lý
  đã ghi trong plan. Muốn đổi thì sửa plan trước khi sửa code.

## Bản đồ tài liệu

| File | Dùng khi |
|---|---|
| `docs/HANDOFF.md` | Bạn đang đọc — tiếp quản dự án |
| `docs/RUNBOOK.md` | Chạy, reset, gỡ lỗi, dọn dẹp |
| `docs/plans/active/p1-nen-tang-ban-xe.md` | Tiến độ, việc tiếp theo, các quyết định |
| `docs/decisions/` | Vì sao chia vai như vậy |
| `AGENTS.md` | Quy ước làm việc chung |
| `README.md` | Tổng quan ngắn |
