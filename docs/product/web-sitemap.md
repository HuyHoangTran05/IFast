# Sitemap và bản đồ tuyến đường của `web/`

Tài liệu này là danh mục trang chính thức của front-end IFast. PRD mô tả *vì sao*
và *hành vi gì*; tài liệu này mô tả *có những trang nào*, *ai sở hữu dữ liệu cho
trang đó*, và *trang đó thuộc giai đoạn nào*.

Ranh giới tham chiếu tới vinfastauto.com: xem
[decision 0002](../decisions/0002-ranh-gioi-tham-chieu-giao-dien.md).

## Nguồn của bản đồ này

Cấu trúc dưới đây được dựng từ ghi chú đối chiếu trong
[plan P1](../plans/active/p1-nen-tang-ban-xe.md) và từ các domain đã có thật
trong `api/`. **Nó chưa được đối chiếu lại trực tiếp với site tham chiếu trong
phiên viết tài liệu này** — site đó chặn truy cập tự động (Cloudflare) và
`robots.txt` đặt `ai-train=no, use=reference`.

Hệ quả bắt buộc: việc đầu tiên của giai đoạn P2 là một người mở site tham chiếu
bằng trình duyệt, đối chiếu bảng dưới đây, và sửa bảng này trước khi viết
component. Không suy đoán thêm tuyến đường nào ngoài bảng này.

## Quy ước

- Tuyến đường đặt tiếng Việt không dấu, khớp phong cách tuyến đường đã có
  (`/xe/[code]`).
- Cột **Nguồn dữ liệu** chỉ được ghi module `api/` đã tồn tại hoặc `stub` nếu
  module mới chỉ là khung. Không có trang nào được phép tự bịa dữ liệu.
- Cột **Giai đoạn**: P2 là luồng tiền đi vào, P3 là dịch vụ quanh xe, P4 là nội
  dung và mạng lưới.

## Bảng tuyến đường

| Tuyến đường | Mục đích | Nguồn dữ liệu | Render | Giai đoạn | Trạng thái |
| --- | --- | --- | --- | --- | --- |
| `/` | Trang chủ: hero dòng xe, khối ưu đãi đang chạy, lối vào đặt cọc và lái thử | `catalog`, `promotions` | SSR/ISR | P2 | Có khung, chưa đúng IA |
| `/xe` | Danh mục ô tô, lọc theo phân khúc và tầm hoạt động | `catalog` | SSR/ISR | P2 | **Đã có** |
| `/xe/[code]` | Chi tiết dòng xe: thông số có kiểu, phiên bản, màu, giá hai mô hình sở hữu | `catalog`, `pricing` | SSR | P2 | **Đã có** |
| `/xe/[code]/cau-hinh` | Chọn phiên bản, màu, kèm pin hoặc thuê pin; hiện giá theo lựa chọn | `catalog`, `pricing`, `promotions` | CSR trên dữ liệu SSR | P2 | Chưa có |
| `/xe/[code]/chi-phi` | Dự toán lăn bánh theo tỉnh, tách rõ từng khoản phí | `pricing` | CSR trên dữ liệu SSR | P2 | Chưa có |
| `/xe/[code]/dat-coc` | Biểu mẫu đặt cọc, hiển thị snapshot trước khi xác nhận | `orders`, `pricing`, `promotions` | CSR | P2 | Chưa có |
| `/dat-coc/[maDon]` | Xác nhận đơn: tra cứu lại đúng snapshot đã chốt | `orders` | SSR, không cache | P2 | Chưa có |
| `/so-sanh` | So sánh tối đa 3 xe theo thông số và giá | `catalog`, `pricing` | CSR | P3 | Chưa có |
| `/chi-phi-van-hanh` | So sánh chi phí vận hành với xe xăng dầu | `pricing` | CSR | P3 | Chưa có |
| `/dich-vu-pin` | Thuê pin: chính sách bảo hành, công thức bồi thường, biểu phí thuê bao | `battery` | SSR/ISR | P3 | Chưa có |
| `/lai-thu` | Đăng ký lái thử theo đại lý và khung giờ | `testdrive` (stub), `dealers` (stub) | CSR | P3 | Chưa có |
| `/dang-nhap` | Đăng nhập bằng số điện thoại và OTP | `auth` (stub) | CSR | P3 | Chưa có |
| `/tai-khoan` | Hồ sơ khách hàng | `users` (stub) | SSR có phiên | P3 | Chưa có |
| `/tai-khoan/don-hang` | Danh sách đơn và trạng thái thanh toán | `orders`, `payments` (stub) | SSR có phiên | P3 | Chưa có |
| `/dai-ly` | Bản đồ và danh sách đại lý, trạm sạc | `dealers` (stub) | SSR/ISR | P4 | Chưa có |
| `/tin-tuc`, `/tin-tuc/[slug]` | Tin tức và bài viết | Chưa có nguồn — cần quyết định CMS | ISR | P4 | Chưa có |
| `/chinh-sach/[slug]` | Bảo hành, đổi trả, quyền riêng tư, điều khoản | Chưa có nguồn — cần quyết định CMS | SSG | P4 | Chưa có |
| `/ho-tro` | Câu hỏi thường gặp và liên hệ | `notifications` (stub) | SSG + CSR form | P4 | Chưa có |

## Khối dùng chung

| Khối | Xuất hiện ở | Ghi chú |
| --- | --- | --- |
| Header + mega menu dòng xe | Mọi trang | Dữ liệu dòng xe lấy một lần, cache theo ISR |
| Footer | Mọi trang | Liên kết tĩnh, không gọi API |
| Thanh chọn tỉnh | `/xe/[code]` trở đi | Tỉnh đã chọn quyết định mọi con số lăn bánh; lưu client-side |
| Khối ưu đãi đang áp dụng | `/`, `/xe`, `/xe/[code]`, luồng đặt cọc | Luôn kèm ngày hiệu lực, không hiển thị ưu đãi hết hạn |
| Dải CTA "Đặt cọc / Lái thử" | Trang chi tiết và trang dịch vụ | CTA đặt cọc chỉ bật khi dòng xe có bảng giá hiệu lực |

## Ràng buộc dữ liệu xuyên suốt

1. Web **không tính tiền**. `web/src/lib/money.ts` chỉ được định dạng, không
   được cộng trừ nhân chia. Mọi con số tiền đến từ `api/` và mang theo nguồn.
2. Mọi màn hình hiện tiền phải hiện được **thời điểm hiệu lực** của con số đó.
3. Trang xác nhận đơn đọc snapshot của đơn, không đọc lại bảng giá.
4. Trang chưa có nguồn dữ liệu (`tin-tuc`, `chinh-sach`) **không được dựng bằng
   nội dung cứng trong code** trước khi có quyết định nguồn nội dung.
