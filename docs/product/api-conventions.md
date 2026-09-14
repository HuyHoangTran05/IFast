# Quy ước API

Chủ sở hữu: R2b (`contracts/` theo decision 0001). Đổi contract cần R1 duyệt.

**Tài liệu này không phải bản đặc tả API.** Đặc tả là
`contracts/openapi.yaml`, sinh từ code. Ở đây là những thứ OpenAPI không diễn
đạt được: ngữ nghĩa tham số, mô hình lỗi, quy ước tiền, và quy trình.

Liên quan: [ARCHITECTURE.md](../ARCHITECTURE.md) · [PRD backend](backend-prd.md)
· [mô hình dữ liệu](data-model.md) · [từ điển thuật ngữ](glossary.md).

## 1. Contract sinh từ code

```bash
python scripts/generate-contract.py          # sinh lại contracts/openapi.yaml
python scripts/generate-contract.py --check  # fail nếu lệch với code — CI chạy lệnh này
cd web && npm run gen:api                    # sinh type TypeScript từ contract
```

Viết tay OpenAPI cho hàng chục domain sẽ lệch khỏi code trong một tuần, và khi đó
R1 code theo một tài liệu sai — tệ hơn là không có tài liệu. Đổi lại, CI chạy
`--check` nên mọi thay đổi contract lộ ra thành diff.

**Luật quy trình:** đổi contract là PR riêng dán nhãn `contract`, cần R1 approve,
không trộn vào PR feature. Decision 0001 đường may 1.

## 2. Đường dẫn hiện có

Chín đường dẫn. Danh sách này là bản chép tay của `contracts/openapi.yaml`; khi
lệch thì **contract đúng**, không phải tài liệu này.

| Phương thức | Đường dẫn | Domain |
| --- | --- | --- |
| GET | `/health` | system |
| GET | `/catalog/models` | catalog |
| GET | `/catalog/models/{code}` | catalog |
| GET | `/pricing/on-road` | pricing |
| GET | `/pricing/running-cost` | pricing |
| GET | `/promotions` | promotions |
| GET | `/battery/assets/{serial}/compensation` | battery |
| POST | `/orders` | orders |
| GET | `/orders/{code}` | orders |

Tiền tố đường dẫn trùng tên domain; đó là quy ước, không phải trùng hợp
(`APIRouter(prefix="/catalog")`).

## 3. `as_of` — tham số quan trọng nhất của API này

Mọi endpoint tính tiền nhận `as_of: date`. Ngữ nghĩa:

- **Bỏ trống** nghĩa là hôm nay **theo giờ Việt Nam** (`api/core/clock.py`), không
  phải theo giờ máy chủ và không phải theo giờ trình duyệt.
- **Truyền vào** nghĩa là "tính như thể hôm đó". Tra cứu lại một đơn cũ phải
  truyền đúng ngày của đơn, nếu không sẽ ra con số của hôm nay.

Đây không phải tham số gỡ lỗi. Nó là cách duy nhất để giải thích lại một con số
đã báo cho khách nhiều tháng trước — ưu đãi đã hết hạn vẫn phải giải thích được
vì sao từng được áp.

Ngoại lệ có chủ ý: `/battery/assets/{serial}/compensation` dùng `incident_on`
thay vì `as_of`, vì công thức bồi thường tra hai mốc thời gian khác nhau và
`incident_on` chỉ là một trong hai. Mốc còn lại lấy từ `formed_on` của chính tài
sản pin.

## 4. Mô hình lỗi — hiện trạng

| Mã | Khi nào | Nguồn |
| --- | --- | --- |
| 200 | Thành công | — |
| 201 | Tạo đơn thành công | `POST /orders` |
| 404 | Không tìm thấy thực thể, **hoặc** không có chính sách phủ mốc thời gian và địa bàn được hỏi | `PricingUnavailable`, `BatteryPolicyUnavailable`, và tra cứu không thấy |
| 422 | Đầu vào hợp lệ về kiểu nhưng vi phạm quy tắc nghiệp vụ | `ValueError` từ service |
| 422 | Sai kiểu dữ liệu | FastAPI/Pydantic tự sinh |

Thân lỗi là định dạng mặc định của FastAPI: một khoá `detail`.

```json
{ "detail": "chưa có biểu phí lăn bánh cho tỉnh XX tại 2026-09-14" }
```

### Ba vấn đề đã biết của mô hình này

1. **404 mang hai nghĩa.** "Không có dòng xe này" và "tỉnh này chưa có biểu phí"
   trả cùng một mã. Client không phân biệt được bằng máy, chỉ phân biệt được bằng
   cách đọc câu tiếng Việt.
2. **Không có mã lỗi máy đọc được.** `detail` là câu tiếng Việt dành cho người.
   `web/` muốn hiện thông báo khác nhau cho hai trường hợp thì phải so khớp chuỗi
   — rất dễ vỡ.
3. **`detail` trả nguyên văn thông báo nội bộ**, kèm `trim_id` và mốc thời gian.
   Xem [SECURITY.md](../SECURITY.md).

Cả ba là **hiện trạng được ghi nhận, không phải thiết kế đã duyệt**. Sửa chúng là
đổi chính sách quan sát được từ bên ngoài, cần authority — câu hỏi Q-B7 trong
[PRD backend](backend-prd.md).

## 5. Quy ước đặt tên

| Quy ước | Ví dụ | Lý do |
| --- | --- | --- |
| Hậu tố `_vnd` cho mọi trường tiền | `list_price_vnd`, `total_vnd` | Đơn vị nằm trong tên, không phải trong tài liệu |
| Hậu tố `_x10` cho đại lượng thập phân | `consumption_kwh_per_100km_x10` | Tránh `float`; 6,5 truyền vào là `65` |
| Hậu tố `_on` cho ngày | `formed_on`, `quoted_on`, `incident_on` | Phân biệt với dấu thời gian đầy đủ |
| Hậu tố `_at` cho dấu thời gian | `created_at` | |
| `effective_from` / `effective_to` | mọi bảng chính sách | `effective_to = null` nghĩa là còn hiệu lực |
| `_code` cho định danh nghiệp vụ | `province_code`, `code` của dòng xe | Phân biệt với `id` là khoá tự tăng |
| snake_case cho mọi trường JSON | | Khớp Python; `web/` nhận type sinh sẵn nên không phải đổi tay |

Khoảng hiệu lực là **nửa mở**: `effective_from <= as_of < effective_to`. Nghĩa là
một chính sách kết thúc ngày 01/01 thì ngày 01/01 đã thuộc về chính sách kế tiếp
(`api/core/effective.py::is_effective_on`).

## 6. Quy ước tiền trên đường truyền

- Tiền là **số nguyên JSON**, đơn vị đồng. Không chuỗi, không số thực, không đơn
  vị nghìn đồng.
- Tổng do máy chủ tính. Client **không được tự cộng** các khoản tách rồi hiển thị
  tổng của mình — nếu hai con số lệch nhau thì lỗi nằm ở client.
- Mỗi phản hồi có tiền đều kèm mốc thời gian đã dùng (`as_of`) và, nơi phù hợp,
  ngày hiệu lực của từng nguồn dữ liệu (`list_price_as_of`, `fuel_price_as_of`,
  `electricity_price_as_of`, `warranty_policy_as_of`).

## 7. Những gì API này chưa có

Ghi rõ để không ai giả định là đã có:

- **Không có xác thực.** Không header, không token. Mọi endpoint công khai.
- **Không có phân trang.** `GET /catalog/models` trả toàn bộ. Sẽ phải thêm, và
  thêm sau là một thay đổi phá vỡ tương thích.
- **Không có lọc hay sắp xếp** trên `/catalog/models`. `web/` lọc phía client.
- **Không có phiên bản API.** Không `/v1`. Câu hỏi Q-B6.
- **Không có idempotency key** cho `POST /orders`. Client gửi trùng sẽ tạo hai
  đơn, trừ khi `code` trùng và vi phạm ràng buộc unique — khi đó lỗi hiện ra là
  lỗi CSDL, không phải một phản hồi có nghĩa. F-13 của [PRD web](web-prd.md) yêu
  cầu chống gửi trùng, nên đây là khoảng trống chặn việc.
- **Không có rate limit.**
- **Không có CORS được cấu hình tường minh.** `web/` chạy khác cổng với `api/`
  nên đây là việc phải làm ở bước 1 của plan P2.

## 8. Khi thêm endpoint mới

1. Viết service là hàm thuần, nhận `as_of` nếu có dính tới tiền hoặc chính sách.
2. Viết test cho service trước khi viết router.
3. Router chỉ đọc dữ liệu, gọi service, ánh xạ lỗi sang HTTP.
4. Đăng ký router bằng cách **thêm dòng ở cuối** khối trong `api/main.py`. Không
   sắp xếp lại khối đó.
5. Chạy `python scripts/generate-contract.py`, commit contract trong PR riêng.
6. Không đặt chính sách quan sát được từ bên ngoài (giới hạn, mặc định, định
   dạng) mà không có authority trong repo.
