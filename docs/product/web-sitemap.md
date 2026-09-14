# Sitemap và bản đồ tuyến đường của `web/`

Tài liệu này là danh mục trang chính thức của front-end IFast. PRD mô tả *vì sao*
và *hành vi gì*; tài liệu này mô tả *có những trang nào*, *ai sở hữu dữ liệu cho
trang đó*, và *trang đó thuộc giai đoạn nào*.

Ranh giới tham chiếu tới vinfastauto.com: xem
[decision 0002](../decisions/0002-ranh-gioi-tham-chieu-giao-dien.md).

## Nguồn của bản đồ này

Cấu trúc IFast được dựng từ các domain đã có thật trong `api/` và được đối
chiếu thủ công ngày 2026-09-14 với các link/CTA công khai từ homepage VinFast.
Người đối chiếu đã mở các trang homepage, detail VF 2, showroom/trạm sạc,
chính sách bảo hành và FAQ/hỗ trợ; không dùng sitemap.xml, crawler hay tự động
enumerate URL.

Đối chiếu này xác nhận IA, interaction và bố cục cấp trang, không cấp quyền
sao chép asset, nội dung marketing, CSS hay source code. Route tham chiếu như
`/cars/:slug` hoặc `/deposit/:vehicle` chỉ mô tả **mô hình IA**; các URL tiếng
Việt trong bảng dưới đây vẫn là authority hiện hành của IFast.

Hành vi sticky và khác biệt mobile của header chưa được quan sát, nên không
được ghi như fact hoặc suy ra khi làm component.

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
| `/` | Trang chủ là discovery surface: hero, card xe, ưu đãi, lối vào đặt cọc | `catalog`, `promotions` | SSR/ISR | P2 | IA đã xác nhận; có khung, chưa đúng IA |
| `/xe` | Danh mục ô tô, lọc theo phân khúc và tầm hoạt động | `catalog` | SSR/ISR | P2 | IA đã xác nhận; **đã có** |
| `/xe/[code]` | Long-form detail: thông số có kiểu, phiên bản, màu, hai mô hình giá, CTA đặt cọc | `catalog`, `pricing` | SSR | P2 | IA đã xác nhận; **đã có** |
| `/xe/[code]/cau-hinh` | Bước đầu funnel: chọn phiên bản, màu, kèm pin hoặc thuê pin; hiện giá theo lựa chọn | `catalog`, `pricing`, `promotions` | CSR trên dữ liệu SSR | P2 | Chưa có |
| `/xe/[code]/chi-phi` | Utility dự toán lăn bánh theo tỉnh, tách rõ từng khoản phí | `pricing` | CSR trên dữ liệu SSR | P2 | Chưa có |
| `/xe/[code]/dat-coc` | Funnel giao dịch: cấu hình → thông tin khách → review snapshot → submit | `orders`, `pricing`, `promotions` | CSR | P2 | Chưa có |
| `/dat-coc/[maDon]` | Xác nhận đơn: tra cứu lại đúng snapshot đã chốt | `orders` | SSR, không cache | P2 | Chưa có |
| `/so-sanh` | So sánh tối đa 3 xe theo thông số và giá | `catalog`, `pricing` | CSR | P3 | Chưa có |
| `/chi-phi-van-hanh` | So sánh chi phí vận hành với xe xăng dầu | `pricing` | CSR | P3 | Chưa có |
| `/dich-vu-pin` | Thuê pin: chính sách bảo hành, công thức bồi thường, biểu phí thuê bao | `battery` | SSR/ISR | P3 | Chưa có |
| `/lai-thu` | Đăng ký lái thử theo đại lý và khung giờ; là form utility riêng | `testdrive` (stub), `dealers` (stub) | CSR | P3 | IA đã xác nhận; chưa có |
| `/dang-nhap` | Đăng nhập bằng số điện thoại và OTP | `auth` (stub) | CSR | P3 | Chưa có |
| `/tai-khoan` | Hồ sơ khách hàng | `users` (stub) | SSR có phiên | P3 | Chưa có |
| `/tai-khoan/don-hang` | Danh sách đơn và trạng thái thanh toán | `orders`, `payments` (stub) | SSR có phiên | P3 | Chưa có |
| `/dai-ly` | Finder đại lý/showroom riêng, có tìm kiếm và lọc địa điểm; không trộn vào hỗ trợ | `dealers` (stub) | SSR/ISR | P4 | IA đã xác nhận; chưa có |
| `/tin-tuc`, `/tin-tuc/[slug]` | Tin tức và bài viết | Chưa có nguồn — cần quyết định CMS | ISR | P4 | Chưa có |
| `/chinh-sach/[slug]` | Bảo hành, đổi trả, quyền riêng tư, điều khoản | Chưa có nguồn — cần quyết định CMS | SSG | P4 | Chưa có |
| `/ho-tro` | Nhóm hỗ trợ: FAQ, bảo hành, dịch vụ và liên hệ | `notifications` (stub) | SSG + CSR form | P4 | IA đã xác nhận; chưa có |

## Khối dùng chung

| Khối | Xuất hiện ở | Ghi chú |
| --- | --- | --- |
| Header + mega menu dòng xe | Trang public: home, danh mục, detail, đại lý và hỗ trợ | Dữ liệu dòng xe lấy một lần, cache theo ISR; funnel đặt cọc có thể dùng header rút gọn nhưng phải còn lối về trang chủ. Sticky/mobile chưa xác nhận. |
| Footer | Trang marketing/nội dung và utility public | Liên kết tĩnh, không gọi API; gồm tối thiểu công ty, xe, đại lý, hỗ trợ, liên hệ, chính sách/quyền riêng tư và copyright. Funnel đặt cọc có thể dùng footer rút gọn. |
| Thanh chọn tỉnh | `/xe/[code]` trở đi | Tỉnh đã chọn quyết định mọi con số lăn bánh; lưu client-side |
| Khối ưu đãi đang áp dụng | `/`, `/xe`, `/xe/[code]`, luồng đặt cọc | Luôn kèm ngày hiệu lực, không hiển thị ưu đãi hết hạn |
| Dải CTA "Đặt cọc / Lái thử" | Trang chi tiết và trang dịch vụ | CTA đặt cọc chỉ bật khi dòng xe có bảng giá hiệu lực |

## CTA tham chiếu cho P2

| Bề mặt | Primary | Secondary / supporting | Hệ quả cho IFast |
| --- | --- | --- | --- |
| Card xe ở trang chủ | Đặt cọc | Xem chi tiết | Card phải dẫn được tới detail và funnel đặt cọc. |
| Chi tiết xe | Đặt cọc | Dự toán chi phí lăn bánh; đăng ký tư vấn khi có API/authority | Detail không chỉ là màn hình checkout; đây là template discovery dùng lại theo dữ liệu xe. |
| Header | Đăng ký lái thử | — | Là CTA toàn cục của reference, nhưng IFast giữ ở P3 vì `testdrive` còn stub. |
| Funnel đặt cọc | Bước tiếp theo | Submit đặt cọc ở bước cuối | Các bước có thể là state trong một route; không coi đặt cọc là trang thông tin tĩnh. |

## Phân biệt scope IFast với reference

- Reference có finder showroom riêng, support sau bán hàng, lái thử và các
  utility độc lập. IFast ghi nhận IA này nhưng chỉ làm trong giai đoạn P3/P4
  khi module API tương ứng có thật.
- Giá có thể xuất hiện ở detail; cấu hình có thể là bước đầu funnel; chi phí
  lăn bánh là utility riêng. Không tạo route giá toàn cục chỉ để bắt chước
  reference.
- IFast giữ guest deposit theo PRD. Không thêm account/login, xe máy điện,
  trạm sạc, phụ kiện hay hệ sinh thái ngoài scope chỉ vì reference có chúng.

## Ràng buộc dữ liệu xuyên suốt

1. Web **không tính tiền**. `web/src/lib/money.ts` chỉ được định dạng, không
   được cộng trừ nhân chia. Mọi con số tiền đến từ `api/` và mang theo nguồn.
2. Mọi màn hình hiện tiền phải hiện được **thời điểm hiệu lực** của con số đó.
3. Trang xác nhận đơn đọc snapshot của đơn, không đọc lại bảng giá.
4. Trang chưa có nguồn dữ liệu (`tin-tuc`, `chinh-sach`) **không được dựng bằng
   nội dung cứng trong code** trước khi có quyết định nguồn nội dung.
