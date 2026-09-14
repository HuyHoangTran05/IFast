# PRD — Trải nghiệm web bán ô tô điện IFast

Ngày: 2026-09-14 · Trạng thái: Bản nháp chờ duyệt · Chủ sở hữu: R1 (frontend)

Tài liệu này là authority cho hành vi quan sát được từ bên ngoài của `web/`.
Khi hành vi đổi, sửa tài liệu này trước khi sửa code.

Tài liệu liên quan:

- [Sitemap và bản đồ tuyến đường](web-sitemap.md) — có những trang nào.
- [PRD backend](backend-prd.md) — API mà các trang này gọi tới.
- [Ngôn ngữ thiết kế](web-design-system.md) — trang trông như thế nào.
- [Decision 0002](../decisions/0002-ranh-gioi-tham-chieu-giao-dien.md) — được
  tham chiếu site ngoài tới đâu.
- [Plan P2](../plans/active/p2-trai-nghiem-ban-xe-tren-web.md) — làm theo thứ tự nào.
- [Plan P1](../plans/active/p1-nen-tang-ban-xe.md) — backend đã có gì.

## 1. Vấn đề

`api/` đã có đủ quy tắc nghiệp vụ để bán một chiếc xe: danh mục, bảng giá theo
thời gian, hai mô hình sở hữu, phí lăn bánh theo tỉnh, ưu đãi có vòng đời, và
đặt cọc có snapshot. 60 test xanh.

`web/` mới có hai trang và chưa từng chạy cùng `api/`. Khách không có đường nào
để đi từ "muốn xem xe" đến "đã đặt cọc". Toàn bộ giá trị của backend hiện không
tới được người dùng.

## 2. Kết quả mong muốn

Một khách hàng Việt Nam, trên điện thoại, kết nối 4G, tự làm được trọn vẹn
chuỗi sau mà không cần gọi ai: tìm dòng xe phù hợp → hiểu mình phải trả bao
nhiêu tại tỉnh của mình → chọn cấu hình và mô hình sở hữu → đặt cọc → nhận mã
đơn tra cứu lại được, với con số không đổi.

## 3. Người dùng và tình huống

| Nhóm | Tình huống điển hình | Điều họ cần thấy trong 30 giây đầu |
| --- | --- | --- |
| Khách lần đầu tìm hiểu xe điện | Vào từ quảng cáo hoặc tìm kiếm, chưa biết gì | Xe nào, giá bao nhiêu, có khác gì xe xăng |
| Khách đã chọn được dòng xe | Quay lại lần 2–3, đang so tiền | Tổng chi phí lăn bánh tại tỉnh mình, ưu đãi còn hiệu lực |
| Khách sẵn sàng xuống tiền | Muốn giữ xe, giữ giá | Nút đặt cọc, số tiền cọc, cam kết giá không đổi |
| Khách đã đặt cọc | Kiểm tra lại đơn | Trạng thái đơn và đúng con số hôm đặt |
| Nhân viên tư vấn tại đại lý | Mở web trước mặt khách | Cùng một con số với khách, tra được nguồn |

## 4. Phạm vi

### Trong phạm vi PRD này (toàn bộ mặt web)

Trang chủ, danh mục ô tô, chi tiết dòng xe, cấu hình, dự toán lăn bánh, đặt cọc,
tra cứu đơn, so sánh xe, so sánh chi phí vận hành, dịch vụ pin, lái thử, tài
khoản khách hàng, mạng lưới đại lý và trạm sạc, tin tức, trang chính sách, hỗ trợ.

### Ngoài phạm vi

- Xe máy điện, phụ kiện, thương mại điện tử (kế thừa ranh giới của plan P1).
- Lưu trữ năng lượng.
- Đặt lịch bảo dưỡng và hậu mãi.
- Thanh toán thật (cổng thanh toán) — yêu cầu một decision riêng trước khi
  viết dòng code nào, theo plan P1 mục 7.
- Trang quản trị nội bộ và CMS.

### Giai đoạn

Phạm vi trên được chia ba đợt. Chỉ **P2** được triển khai ngay; P3 và P4 nằm
trong PRD để thiết kế không phải làm lại, nhưng chưa được mở.

| Giai đoạn | Nội dung | Điều kiện mở |
| --- | --- | --- |
| P2 | Luồng tiền đi vào: trang chủ → danh mục → chi tiết → cấu hình → chi phí → đặt cọc → xác nhận, cộng design system | Bắt đầu ngay |
| P3 | Lái thử, đăng nhập, tài khoản và đơn hàng, dịch vụ pin, so sánh | Sau khi P2 có E2E xanh và các module stub `auth`, `users`, `testdrive` có API thật |
| P4 | Đại lý và trạm sạc, tin tức, chính sách, hỗ trợ | Sau khi có quyết định nguồn nội dung (CMS) và nguồn dữ liệu đại lý |

## 5. Yêu cầu chức năng

Ký hiệu: **F-nn**. Mỗi yêu cầu có tiêu chí chấp nhận kiểm chứng được bằng máy
hoặc quan sát được trên giao diện thật.

### 5.1 Tìm và hiểu xe (P2)

**F-01 — Danh mục xe.** `/xe` liệt kê mọi dòng xe đang bán, lấy từ `api/catalog`.
Mỗi thẻ xe hiện: tên, phân khúc, tầm hoạt động, giá khởi điểm và mô hình sở hữu
của giá đó.
*Chấp nhận:* số thẻ hiển thị bằng đúng số dòng xe API trả về; không thẻ nào
thiếu giá trừ khi API không có bảng giá hiệu lực, khi đó hiện "Liên hệ" chứ
không hiện 0.

**F-02 — Lọc và sắp xếp.** Lọc theo phân khúc và khoảng giá; sắp xếp theo giá
tăng hoặc tầm hoạt động giảm. Trạng thái lọc nằm trong URL.
*Chấp nhận:* dán lại URL đã lọc ở tab mới cho ra đúng cùng kết quả.

**F-03 — Chi tiết dòng xe.** `/xe/[code]` hiện thông số có kiểu dữ liệu theo
nhóm, thư viện ảnh, danh sách phiên bản và màu, và **hai cột giá**: kèm pin và
thuê pin, mỗi cột ghi rõ điều gì đã gồm trong giá.
*Chấp nhận:* hai mô hình sở hữu luôn hiện cạnh nhau, không bao giờ chỉ hiện một.

**F-04 — Cấu hình xe.** Chọn phiên bản, màu ngoại thất, mô hình sở hữu. Giá cập
nhật theo lựa chọn, lấy lại từ API, không tính ở client.
*Chấp nhận:* mỗi lần đổi lựa chọn, con số hiển thị khớp byte-for-byte với giá
trị API trả về cho tổ hợp đó.

### 5.2 Hiểu chi phí (P2)

**F-05 — Chọn tỉnh.** Khách chọn tỉnh; lựa chọn được nhớ giữa các trang và giữa
các phiên trên cùng trình duyệt. Mặc định **không đoán** tỉnh; khi chưa chọn thì
hiện rõ "chưa chọn tỉnh" thay vì lặng lẽ dùng Hà Nội.
*Chấp nhận:* đổi tỉnh trên trang chi tiết thì trang chi phí và trang đặt cọc
dùng đúng tỉnh mới.

**F-06 — Dự toán lăn bánh.** Hiện bảng tách khoản: giá xe, lệ phí trước bạ, phí
đăng ký biển số, phí đường bộ, bảo hiểm bắt buộc, tổng. Mỗi khoản ghi căn cứ và
ngày hiệu lực.
*Chấp nhận:* cùng dòng xe, hai tỉnh khác nhau cho hai tổng khác nhau; cùng tỉnh,
hai mốc thời gian khác nhau cho hai tổng khác nhau — khớp với chứng cứ đã ghi
trong plan P1.

**F-07 — Nhãn dữ liệu mẫu.** Khi API báo biểu phí đang dùng là dữ liệu mẫu chưa
đối chiếu pháp lý, giao diện phải hiện cảnh báo rõ ràng, không ẩn.
*Chấp nhận:* tắt cờ dữ liệu mẫu thì cảnh báo biến mất; bật thì mọi trang có
tiền đều hiện.

**F-08 — Ưu đãi đang áp dụng.** Hiện ưu đãi còn hiệu lực kèm ngày kết thúc và
số tiền giảm. Không hiện ưu đãi đã hết hạn hoặc chưa bắt đầu.
*Chấp nhận:* một ưu đãi hết hạn hôm nay biến mất khỏi giao diện đúng theo ngày
nghiệp vụ giờ Việt Nam, không theo giờ trình duyệt.

**F-09 — So sánh chi phí vận hành (P3).** So chi phí nhiên liệu và bảo dưỡng với
xe xăng theo số km/năm khách nhập.

### 5.3 Đặt cọc (P2)

**F-10 — Biểu mẫu đặt cọc.** Thu họ tên, số điện thoại, email, tỉnh, đại lý
nhận xe. Validate phía client và phía server; lỗi hiện ngay tại trường.
*Chấp nhận:* số điện thoại sai định dạng không gửi được; server từ chối thì lỗi
hiện đúng trường chứ không phải một thông báo chung.

**F-11 — Xác nhận trước khi chốt.** Trước khi gửi, hiện toàn bộ snapshot: dòng
xe, phiên bản, màu, mô hình sở hữu, tỉnh, từng khoản chi phí, ưu đãi áp dụng,
tiền cọc, tổng. Khách phải xác nhận chủ động.
*Chấp nhận:* không có đường nào tạo đơn mà bỏ qua màn hình này.

**F-12 — Giá không đổi sau khi chốt.** Trang tra cứu đơn hiện đúng snapshot lúc
đặt, kể cả khi bảng giá đã đổi sau đó.
*Chấp nhận:* kịch bản E2E — đặt đơn, tăng giá trong `api/pricing`, mở lại trang
đơn, con số không đổi; báo giá mới trên trang xe thì đổi.

**F-13 — Chống gửi trùng.** Bấm gửi hai lần hoặc tải lại trang sau khi gửi
không tạo đơn thứ hai.
*Chấp nhận:* gửi lại cùng khoá idempotency trả về đúng đơn cũ.

**F-14 — Tra cứu đơn.** `/dat-coc/[maDon]` mở được bằng mã đơn, không cần đăng
nhập ở P2, và không cache.

### 5.4 Các mảng còn lại (P3, P4)

**F-15** Đăng ký lái thử theo đại lý và khung giờ. **F-16** Đăng nhập OTP theo
số điện thoại. **F-17** Danh sách đơn trong tài khoản. **F-18** Dịch vụ pin:
chính sách bảo hành và công thức bồi thường có sàn 10%. **F-19** So sánh tối đa
3 xe. **F-20** Bản đồ đại lý và trạm sạc. **F-21** Tin tức và trang chính sách.

Các yêu cầu này chỉ được chi tiết hoá khi giai đoạn tương ứng mở, và chỉ sau khi
module `api/` tương ứng thôi là stub.

## 6. Yêu cầu phi chức năng

**N-01 — Hiệu năng.** Trên Moto G Power giả lập, mạng 4G chậm: LCP ≤ 2,5 giây,
CLS ≤ 0,1, INP ≤ 200 ms ở `/`, `/xe`, `/xe/[code]`. Đo bằng Lighthouse CI.

**N-02 — Thiết bị.** Hoạt động đúng từ bề rộng 360 px. Không có thanh cuộn
ngang ở bất kỳ bề rộng nào.

**N-03 — Tiếp cận.** WCAG 2.1 mức AA: tương phản, thứ tự tiêu đề, nhãn cho mọi
trường nhập, thao tác được trọn vẹn bằng bàn phím, focus nhìn thấy được.

**N-04 — SEO.** Trang danh mục và chi tiết render phía máy chủ, có `<title>`,
mô tả, canonical, Open Graph, và dữ liệu có cấu trúc cho sản phẩm.

**N-05 — Ngôn ngữ.** Tiếng Việt là mặc định. Kiến trúc phải cho phép thêm tiếng
Anh sau mà không viết lại trang; **không** dựng trang tiếng Anh ở P2.

**N-06 — Tiền tệ.** Hiển thị đồng Việt Nam, số nguyên, phân tách hàng nghìn theo
chuẩn Việt Nam. Không làm tròn ở client.

**N-07 — Trạng thái lỗi.** Mỗi màn hình gọi API có ba trạng thái vẽ được: đang
tải, lỗi có hành động thử lại, và rỗng. Không màn hình trắng.

**N-08 — Bí mật.** Không khoá, không token nhà cung cấp trong bundle client.
Mọi biến môi trường lộ ra client phải có tiền tố tường minh và được liệt kê
trong runbook.

**N-09 — Kiểu dữ liệu.** Type của API sinh từ `contracts/openapi.yaml` bằng
`npm run gen:api`. Không khai báo tay type cho phản hồi API.

## 7. Ràng buộc kỹ thuật kế thừa

Bốn bất biến của plan P1 áp vào web như sau:

1. Con số tiền đi kèm thời điểm hiệu lực → giao diện phải chỗ nào cũng hiện được
   ngày hiệu lực.
2. Tiền là số nguyên đồng → client chỉ định dạng, tuyệt đối không tính toán.
3. Đơn đã chốt giữ snapshot → trang đơn đọc snapshot, không đọc bảng giá.
4. Mọi con số mang theo nguồn → thành phần hiển thị tiền nhận cả giá trị lẫn
   nguồn, không nhận riêng con số.

Stack giữ nguyên theo quyết định P1: Next.js + TypeScript, type sinh từ contract.

## 8. Đo lường thành công

| Chỉ số | Ngưỡng | Cách đo |
| --- | --- | --- |
| Luồng đặt cọc chạy đầu-cuối | E2E xanh trong CI | `tests/e2e/` |
| Sai lệch con số web và API | 0 trường hợp | Assert trong E2E so với phản hồi API |
| Core Web Vitals | Đạt N-01 | Lighthouse CI trên 3 tuyến đường |
| Lỗi tiếp cận nghiêm trọng | 0 | axe trong CI |
| Kiểu dữ liệu và build | Xanh | `npm run typecheck && npm run build` |

## 9. Câu hỏi còn mở — cần quyết định trước khi chạm tới phần liên quan

| # | Câu hỏi | Chặn phần nào | Ai quyết |
| --- | --- | --- | --- |
| Q1 | Nguồn ảnh và nội dung marketing cho trang chủ và chi tiết xe là gì? | F-01, F-03, toàn bộ P2 visual | Sản phẩm |
| Q2 | Nguồn nội dung cho tin tức và trang chính sách: CMS nào, hay Markdown trong repo? | P4 | Sản phẩm + R4a |
| Q3 | Dữ liệu đại lý và trạm sạc lấy từ đâu, nhà cung cấp bản đồ nào? | F-20 | R2b + R4a |
| Q4 | Tiền cọc là số cố định hay theo phần trăm giá xe, chính sách hoàn cọc? | F-11, F-12 | Sản phẩm + pháp lý |
| Q5 | Có yêu cầu đăng nhập mới được đặt cọc không? | F-10, F-14, F-16 | Sản phẩm |
| Q6 | Khi nào thay biểu phí mẫu bằng biểu phí pháp lý? | F-07 và điều kiện lên production | Sản phẩm + R2a |

Không được chọn mặc định thay cho các câu hỏi này trong lúc viết code. Mặc định
cấu hình được không phải là authority.

## 10. Điều kiện hoàn tất P2

P2 xong khi: mọi yêu cầu F-01 đến F-14 đạt tiêu chí chấp nhận; N-01 đến N-09 có
chứng cứ đo được; E2E luồng đặt cọc xanh trong CI; và bảng sitemap đã được một
người đối chiếu với site tham chiếu, không còn tuyến đường nào ở trạng thái suy
đoán.
