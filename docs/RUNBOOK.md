# Application Runbook: IFast

Cách chạy và kiểm chứng IFast trên máy phát triển. Mọi lệnh trong tài liệu này
đã được chạy thật; chỗ nào chưa kiểm chứng đều nằm ở mục Chưa kiểm chứng.

## Scope

Hai bề mặt:

- **API** (`api/`) — FastAPI, phục vụ danh mục xe, giá, ưu đãi, pin, đơn hàng.
- **Web** (`web/`) — Next.js, đọc dữ liệu từ API.

Runbook này phục vụ: chạy lần đầu, chạy lại hằng ngày, và chạy bộ kiểm chứng
trước khi mở PR.

## Prerequisites

| Thứ | Phiên bản đã kiểm chứng | Bắt buộc |
|---|---|---|
| Python | 3.13.9 (yêu cầu tối thiểu 3.11) | Có |
| Node.js | 22.19.0 | Chỉ khi làm web |
| npm | 10.9.3 | Chỉ khi làm web |
| Docker | 29.5.3 | Chỉ khi chạy PostgreSQL |

Không cần khoá API hay dịch vụ ngoài nào. `ai/` chưa gọi nhà cung cấp mô hình
thật nên không cần khoá LLM.

**Bắt buộc dùng virtualenv.** Không cài dependency vào Python hệ thống. Trên
Windows, `python` và `pip` rất dễ trỏ vào hai interpreter khác nhau, và khi đó
bạn cài gói ở một nơi rồi chạy ở nơi khác mà vẫn tưởng đã kiểm chứng.

## Start

### API

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -e ".[dev]"
python scripts/seed-dev.py      # tạo bảng và nạp dữ liệu mẫu
uvicorn api.main:app --reload
```

- Cổng: **8000** (mặc định của uvicorn, đổi bằng `--port`).
- Trạng thái ghi: **`ifast.db`** ở gốc repo — SQLite, đã bị gitignore.
- CSDL: mặc định SQLite. Đặt `IFAST_DATABASE_URL` để đổi sang PostgreSQL, ví dụ
  `postgresql+psycopg://ifast:ifast_dev_only@localhost:5432/ifast`.

### Web

```bash
cd web
npm install
npm run dev
```

- Cổng: **3000**.
- Web đọc API tại `IFAST_API_BASE_URL`, mặc định `http://localhost:8000`.

### Cả stack bằng PostgreSQL

```bash
docker compose -f infra/docker-compose.yml up --build
```

Dựng 2 service: `db` (postgres:16-alpine, cổng 5432) và `api` (cổng 8000).
Dữ liệu nằm trong volume `db_data`.

**Chưa kiểm chứng:** compose mới chỉ được `docker compose config` xác nhận cú
pháp hợp lệ, chưa chạy `up` thật. Xem mục Chưa kiểm chứng.

## Readiness

- **API sẵn sàng** khi `curl -s http://localhost:8000/health` trả
  `{"status":"ok"}`. Tài liệu tương tác ở `http://localhost:8000/docs`.
- **Web sẵn sàng** khi Next.js in dòng `Ready in ...` và `http://localhost:3000`
  trả HTTP 200.

Nếu API chạy nhưng chưa nạp dữ liệu, `GET /catalog/models` trả mảng rỗng chứ
không lỗi — chạy `python scripts/seed-dev.py`.

## Deterministic State

Toàn bộ trạng thái phát triển nằm trong một file duy nhất: `ifast.db` ở gốc
repo. Không có state nào nằm ngoài thư mục dự án.

Reset sạch:

```bash
rm -f ifast.db && python scripts/seed-dev.py
```

Dữ liệu mẫu nạp vào: dòng xe VF 2 (một phiên bản, hai màu), bảng giá kèm pin và
thuê pin, biểu phí lăn bánh cho HN và HCM với hai mốc hiệu lực, giá xăng dầu và
giá điện tham chiếu, hai ưu đãi, chính sách bảo hành pin, và một pin thuê mẫu
mã `PIN-VF2-0001`.

> Biểu phí lăn bánh, giá điện và giá nhiên liệu trong `api/seed.py` là **dữ
> liệu mẫu chưa đối chiếu pháp lý**. Đủ để chạy và để test, không được dùng làm
> số liệu thật.

## Interface

Bốn lệnh đủ để thấy các quy tắc nghiệp vụ chính hoạt động:

```bash
# Thông số có kiểu dữ liệu
curl -s "http://localhost:8000/catalog/models/VF2"

# Dự toán lăn bánh — đổi province_code sẽ ra con số khác
curl -s "http://localhost:8000/pricing/on-road?trim_id=1&province_code=HN&as_of=2026-06-01"

# Bồi thường pin thuê — đổi incident_on sẽ thấy sàn 10% chặn lại
curl -s "http://localhost:8000/battery/assets/PIN-VF2-0001/compensation?incident_on=2028-01-01"

# Đặt cọc, đơn giữ snapshot giá
curl -s -X POST http://localhost:8000/orders -H "Content-Type: application/json" \
  -d '{"code":"DH-001","trim_id":1,"province_code":"HN","deposit_vnd":10000000,"as_of":"2026-06-01"}'
```

Danh sách endpoint đầy đủ: `http://localhost:8000/docs` hoặc
`contracts/openapi.yaml`.

## Runtime Evidence

- API ghi log truy cập ra stdout của tiến trình uvicorn. Không có file log.
- Lỗi nghiệp vụ trả về HTTP có ý nghĩa, không phải 500: **404** khi thiếu dữ
  liệu (tỉnh chưa có biểu phí, dòng xe không tồn tại), **422** khi đầu vào sai
  (tiền cọc lớn hơn giá trị đơn).
- Thông báo lỗi viết bằng tiếng Việt và nêu rõ mốc thời gian đã tra, ví dụ
  `chưa có biểu phí lăn bánh cho tỉnh DN tại 2026-06-01`.
- **Chưa có** correlation id, structured logging, hay tracing. Xem Chưa kiểm chứng.

Trên Windows, console mặc định là cp1252 và sẽ ném `UnicodeEncodeError` khi in
tiếng Việt có dấu. Đặt `PYTHONIOENCODING=utf-8` trước khi chạy script tự viết.
Các script trong `scripts/` đã tự ép UTF-8.

## Ownership And Cleanup

Một lần chạy phát triển tạo ra đúng ba thứ, tất cả đều trong thư mục dự án:

| Thứ | Dọn bằng |
|---|---|
| `ifast.db` | `rm -f ifast.db` |
| `.venv/` | `rm -rf .venv` |
| `web/node_modules/`, `web/.next/` | `rm -rf web/node_modules web/.next` |

Khi dùng Docker: `docker compose -f infra/docker-compose.yml down -v` xoá cả
volume `db_data`. Bỏ `-v` nếu muốn giữ dữ liệu.

Không có tài nguyên nào được tạo bên ngoài thư mục dự án.

## Validation

Chạy trong venv đã kích hoạt. Đây đúng là bộ mà CI chạy:

```bash
python -m pytest                                    # 60 test
python scripts/generate-contract.py --check         # contract khớp backend
python -m ruff check api ai alembic scripts
python -m ruff format --check api ai alembic scripts

cd web && npm run typecheck && npm run build
```

### Kiểm tra sức khoẻ harness

Binary `harness` phụ thuộc nền tảng nên bị gitignore — clone mới **không có
sẵn** nó. Lấy về theo một trong hai cách:

```bash
# Cách 1: tải bản phát hành đã ký checksum (khuyến nghị, không cần Rust)
TAG=harness-v0.1.10
BASE=https://github.com/hoangnb24/repository-harness/releases/download/$TAG
curl -fsSL "$BASE/harness-windows-x64.exe"        -o scripts/bin/harness.exe
curl -fsSL "$BASE/harness-windows-x64.exe.sha256" -o /tmp/h.sha256
sha256sum scripts/bin/harness.exe          # phải khớp nội dung /tmp/h.sha256
# macOS/Linux: đổi tên asset thành harness-macos-arm64, harness-linux-x64, ...
```

```bash
# Cách 2: build từ source đã vendor trong repo (cần cài Rust)
cargo build --manifest-path repository-harness/Cargo.toml -p harness --locked
cp repository-harness/target/debug/harness scripts/bin/harness
```

Chạy installer từ `repository-harness/` mà **không** có `cargo` sẽ fail — nó
vào chế độ local source và gọi `cargo build`.

Sau khi có binary:

```bash
scripts/bin/harness.exe status --directory .        # Windows
scripts/bin/harness status --directory .            # macOS / Linux
```

Báo `modified` khác 0 là bình thường. Harness quản lý `docs/README.md` và
`docs/decisions/README.md`, và cả hai đã được sửa có chủ ý để thêm mục lục cho
tài liệu của IFast. Harness hỗ trợ sửa đổi phía người dùng và sẽ merge ba
chiều khi cập nhật.

Xem chính xác file nào đang lệch:

```bash
scripts/bin/harness.exe doctor --directory .
```

## Chưa kiểm chứng

Những mục dưới đây **chưa từng chạy thật**. Đừng viết tài liệu cho chúng như
thể đã hoạt động, và đừng suy đoán hành vi.

- `docker compose up` — mới chỉ xác nhận cú pháp bằng `docker compose config`.
- `alembic upgrade head` trên **PostgreSQL** — mới chỉ chạy trên SQLite.
- **Web và API chạy cùng lúc.** Web build và typecheck xanh, nhưng chưa có lần
  nào trang thật gọi API thật. Đây là việc nên làm đầu tiên khi tiếp quản.
- Quan sát vận hành: chưa có log có cấu trúc, chưa có correlation id, chưa có
  tracing, chưa có cảnh báo chi phí cho `ai/`.
- Không có môi trường staging hay production. Chưa có quy trình deploy.
