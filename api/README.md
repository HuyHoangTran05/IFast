# api — Backend API

Chia theo **domain dọc**, không chia theo tầng. Mỗi domain sở hữu trọn router +
service + model + test + migration của bảng thuộc domain đó.
Một feature = một domain = một PR = một người.

| Thư mục | Chủ |
|---|---|
| `catalog/` `pricing/` `promotions/` `inventory/` `battery/` `dealers/` | **R2a — Sản phẩm & giá** ("bán cái gì, giá bao nhiêu") |
| `orders/` `payments/` `testdrive/` `users/` `auth/` `notifications/` | **R2b — Khách hàng & giao dịch** ("ai mua, mua thế nào") |

## Ranh giới giữa R2a và R2b

Hẹp có chủ đích. Khi tạo đơn, `orders/` **chụp snapshot** giá, ưu đãi đang áp
dụng và cấu hình xe vào chính đơn hàng, rồi không đọc lại `pricing/` nữa. Giá
đổi về sau không được làm đổi đơn đã chốt — vừa đúng nghiệp vụ, vừa cắt phụ
thuộc giữa hai người.

## Một sợi chỉ xuyên suốt: chính sách có hiệu lực theo thời gian

Khảo sát trang VinFast thật cho thấy gần như mọi con số đều gắn với một mốc
thời gian: giá niêm yết và giá ưu đãi, ưu đãi miễn phí sạc có ngày bắt đầu,
giá nhiên liệu tham chiếu cập nhật theo ngày, giá pin công bố, thời gian bảo
hành theo chính sách tại thời điểm hình thành tài sản.

Vì vậy **mặc định của hệ thống này là: mọi bảng chính sách và bảng giá đều có
ngày hiệu lực, và mọi phép tính đều nhận một mốc thời gian làm tham số.**
Đừng bao giờ viết hàm tính tiền chỉ đọc "giá hiện tại".

## Shared files

R2b sở hữu, **append-only** — chỉ thêm dòng ở cuối, không sắp xếp lại:

- entrypoint đăng ký router
- config / settings
- `.env.example`

## Migration

Hai người cùng tạo migration sẽ gãy revision chain. Khi conflict, **xoá
migration của mình, pull, generate lại**. Không sửa tay `down_revision`.

## Phạm vi giai đoạn sau

VinFast thật còn có xe máy điện, phụ kiện (thương mại điện tử), dịch vụ hậu
mãi và đặt lịch bảo dưỡng, lưu trữ năng lượng, tin tức/CMS. **Không nằm trong
phạm vi giai đoạn đầu.** Xem `docs/decisions/` để biết vì sao.

Riêng hai chỗ sau cần chừa đường ngay từ đầu vì sửa sau rất đắt:

- `catalog/` nên mô hình hoá được **nhiều loại sản phẩm có schema thông số
  khác nhau** (ô tô tính bằng kW và km NEDC, xe máy tính bằng W và km/lần sạc).
- `orders/` nên phân biệt được **hai luồng mua**: đặt cọc (ô tô) và mua thẳng
  (xe máy, phụ kiện).
