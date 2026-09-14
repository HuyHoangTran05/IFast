# Ngôn ngữ thiết kế của `web/`

Chủ sở hữu: R1. Tài liệu này tồn tại để mỗi trang không tự chế một kiểu riêng.
Khi một quy tắc ở đây mâu thuẫn với một màn hình cụ thể, sửa tài liệu trước,
đừng lặng lẽ phá lệ trong một file component.

Ranh giới được phép tham chiếu từ site ngoài:
[decision 0002](../decisions/0002-ranh-gioi-tham-chieu-giao-dien.md). Tóm tắt:
mượn bố cục, không mượn tài sản thị giác.

## 1. Nguyên tắc

1. **Con số tiền là nội dung quan trọng nhất trên trang.** Mọi lựa chọn kiểu
   chữ, khoảng trắng, tương phản phải phục vụ việc đọc đúng một con số tiền.
2. **Không bao giờ hiện một con số tiền mà không hiện được nó có hiệu lực từ
   khi nào.** Đây là hệ quả trực tiếp của bất biến 1 trong
   [plan P1](../plans/active/p1-nen-tang-ban-xe.md).
3. **Ba trạng thái là bắt buộc, không phải tuỳ chọn.** Component nào gọi dữ liệu
   thì component đó có Loading, Error kèm hành động thử lại, và Empty.
4. **Điện thoại trước.** Thiết kế ở 360 px rồi mới mở rộng.

## 2. Token

Khai báo một lần bằng CSS custom properties ở `web/src/app/globals.css`. Không
hard-code màu hay khoảng cách trong component.

### Màu

| Token | Vai trò |
| --- | --- |
| `--bg` / `--fg` | Nền và chữ mặc định của vùng nội dung, nền sáng |
| `--bg-inverse` / `--fg-inverse` | Hero và footer, nền tối |
| `--surface` / `--border` | Thẻ, bảng, đường phân cách |
| `--brand` / `--brand-fg` | CTA chính: đặt cọc, lái thử |
| `--accent` | Nhãn ưu đãi |
| `--warning` / `--warning-bg` | Cảnh báo dữ liệu mẫu (F-07) |
| `--danger` | Lỗi biểu mẫu và lỗi tải dữ liệu |
| `--muted-fg` | Chú thích, ngày hiệu lực, nguồn số liệu |

Ràng buộc: mọi cặp chữ-trên-nền phải đạt tương phản WCAG AA (4.5:1 cho chữ
thường, 3:1 cho chữ lớn). Cặp nào không đạt thì đổi token, không đổi ngoại lệ.

Chưa chốt giá trị hex cụ thể — phụ thuộc bộ nhận diện IFast, gắn với câu hỏi mở
Q1 trong [PRD](web-prd.md).

### Kiểu chữ

Thang: `12 / 14 / 16 / 20 / 24 / 32 / 40 / 56`. Thân bài 16 px, không nhỏ hơn.
Con số tiền dùng chữ số đều bề rộng (`font-variant-numeric: tabular-nums`) để
cột giá không nhảy khi giá đổi.

Font phải có sẵn bộ dấu tiếng Việt đầy đủ. Không tải font từ site tham chiếu.

### Khoảng cách

Thang 4 px: `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96`. Không dùng giá trị lẻ.

### Breakpoint

`360` (cơ sở) · `768` (máy tính bảng) · `1024` (laptop) · `1440` (màn rộng).
Không có thanh cuộn ngang ở bất kỳ bề rộng nào (N-02).

### Bo góc và bóng

Hai mức bo: `8px` cho phần tử nhỏ, `16px` cho thẻ và khối lớn. Hai mức bóng:
một cho thẻ nổi, một cho lớp phủ. Không thêm mức thứ ba.

## 3. Component cần cho giai đoạn P2

| Component | Trách nhiệm | Ràng buộc cứng |
| --- | --- | --- |
| `SiteHeader` | Điều hướng + mega menu dòng xe | Dữ liệu dòng xe lấy sẵn khi render máy chủ, không gọi API lúc mở menu |
| `SiteFooter` | Liên kết tĩnh | Không gọi API |
| `VehicleCard` | Thẻ xe trong danh mục | Nhận `PriceBlock`, không tự dựng chuỗi giá |
| `SpecTable` | Bảng thông số theo nhóm | Nhận thông số đã có kiểu từ `api/catalog`, không parse chuỗi |
| `PriceBlock` | Hiện một con số tiền | **Nhận cả giá trị lẫn nguồn và ngày hiệu lực. Không nhận số trần.** |
| `OwnershipToggle` | Chuyển giữa kèm pin và thuê pin | Mỗi lần chuyển gọi lại API, không tính ở client |
| `ProvincePicker` | Chọn tỉnh | Không đoán tỉnh mặc định; trạng thái "chưa chọn" là hợp lệ (F-05) |
| `CostBreakdown` | Bảng tách khoản lăn bánh | Mỗi dòng có căn cứ và ngày hiệu lực (F-06) |
| `SampleDataBanner` | Cảnh báo biểu phí mẫu | Hiện khi API báo cờ dữ liệu mẫu, không ẩn được (F-07) |
| `PromoBadge` | Ưu đãi đang áp dụng | Luôn kèm ngày kết thúc; không render ưu đãi ngoài hiệu lực (F-08) |
| `CTABar` | Dải đặt cọc / lái thử | Nút đặt cọc tắt khi dòng xe không có bảng giá hiệu lực |
| `FormField` | Trường nhập có nhãn và lỗi | Lỗi server phải gắn được vào đúng trường (F-10) |
| `OrderSummary` | Snapshot trước khi chốt | Hiện đủ mọi khoản; không có đường tắt bỏ qua (F-11) |
| `LoadingState` / `ErrorState` / `EmptyState` | Ba trạng thái | Bắt buộc ở mọi màn hình gọi API (N-07) |

## 4. Quy tắc về tiền trong giao diện

Đây là phần dễ sai nhất và là phần có rủi ro pháp lý, nên viết thành luật:

1. `web/src/lib/money.ts` **chỉ định dạng**. Không cộng, trừ, nhân, chia, không
   làm tròn. Mọi phép tính nằm ở `api/`.
2. Component hiển thị tiền nhận một đối tượng có giá trị, đơn vị, nguồn, và
   ngày hiệu lực — không nhận `number`.
3. Không có tổng nào được ghép ở client từ nhiều lời gọi API. Tổng do API trả về.
4. Đơn vị là đồng Việt Nam, số nguyên, phân tách hàng nghìn theo chuẩn Việt Nam.
5. Trang tra cứu đơn đọc snapshot của đơn. Không gọi `api/pricing` ở trang đó.

Luật 1 nên được cơ chế hoá bằng một kiểm tra máy móc, theo
[pattern mã hoá bất biến](../patterns/encoding-invariants.md), chứ không chỉ ghi
trong tài liệu này. Cách làm cụ thể để lại cho plan P2 quyết định.

## 5. Ảnh và chuyển động

- Dùng `next/image`. Mỗi ảnh khai báo kích thước để không gây dịch chuyển bố cục
  (CLS ≤ 0,1 theo N-01).
- Ngân sách: ảnh hero ≤ 200 KB sau nén, ảnh thẻ xe ≤ 60 KB. Định dạng hiện đại
  trước, có phương án dự phòng.
- Không animation nào chặn nội dung chính hiện ra. Tôn trọng
  `prefers-reduced-motion`.
- Mọi ảnh có `alt` mô tả được nội dung, không để rỗng trừ ảnh trang trí thuần tuý.

## 6. Tiếp cận

Theo N-03: WCAG 2.1 AA. Cụ thể trong mọi component:

- Thứ tự tiêu đề `h1..h6` liền mạch, mỗi trang một `h1`.
- Mọi trường nhập có `<label>` gắn thật, không chỉ placeholder.
- Thao tác trọn vẹn bằng bàn phím; vòng focus nhìn thấy rõ, không bị `outline: none`.
- Vùng bấm tối thiểu 44×44 px.
- Thông báo lỗi và trạng thái tải được đọc bởi trình đọc màn hình.

## 7. Cái chưa chốt

- Giá trị màu, font chữ, và bộ icon — chờ bộ nhận diện IFast (Q1 trong PRD).
- Có dùng thư viện CSS hay viết CSS Modules thuần — quyết định ở bước 3 của
  [plan P2](../plans/active/p2-trai-nghiem-ban-xe-tren-web.md), sau khi đã biết
  số component thực sự cần.

Không chọn thay cho hai mục này trong lúc viết component. Mặc định cấu hình được
không phải là authority.
