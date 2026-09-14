# 0002 Ranh giới tham chiếu giao diện từ site bên ngoài

Date: 2026-09-14

## Status

Accepted

## Context

Yêu cầu đặt ra là "clone trang vinfastauto.com". Cụm từ đó có ít nhất ba nghĩa
khác hẳn nhau: sao chép nguyên trạng cả thương hiệu, dựng lại cấu trúc nhưng
thay nội dung, hoặc chỉ mượn phong cách thị giác. Ba nghĩa dẫn tới ba sản phẩm
khác nhau và ba mức rủi ro pháp lý khác nhau.

IFast là một sản phẩm bán ô tô điện thật: có bảng giá, có đơn hàng, có tiền
khách chuyển. Một sản phẩm như vậy mang nhãn hiệu của doanh nghiệp khác không
phải là chuyện có thể sửa sau.

Thêm hai dữ kiện kỹ thuật quan sát được trong phiên ngày 2026-09-14:

- `curl` tới `https://vinfastauto.com/vn/sitemap.xml` trả về trang chặn của
  Cloudflare (`IM_UNDER_ATTACK_BOX`), không trả về sitemap.
- `robots.txt` của site đó đặt `Content-Signal: search=yes, ai-train=no,
  use=reference` — tức chủ site cho phép tham chiếu, từ chối dùng để huấn luyện.

Nếu không chốt ranh giới, mỗi người làm web sẽ tự chọn một mức khác nhau, và
những asset tải về sẽ lẫn vào `web/public/` mà không ai truy được nguồn.

## Decision

IFast **tham chiếu cấu trúc, không sao chép nội dung**.

Được phép lấy từ site tham chiếu:

- Cấu trúc thông tin: có những nhóm trang nào, trang nào thuộc nhóm nào.
- Thứ tự các bước trong luồng người dùng, ví dụ xem xe → chọn cấu hình → xem
  chi phí → đặt cọc.
- Kiểu bố cục và mật độ thông tin của từng loại trang.
- Quy ước đặt tên tuyến đường và cách tổ chức điều hướng.

Không được phép đưa vào repo hay vào sản phẩm:

- Logo, nhãn hiệu, tên thương mại, tên dòng xe của doanh nghiệp khác.
- Ảnh, video, icon, font bản quyền tải về từ site đó.
- Văn bản marketing, mô tả sản phẩm, điều khoản, chính sách sao chép nguyên văn.
- File CSS, JS, hay bundle tải về từ site đó, kể cả để "tham khảo".

Cách xác minh cấu trúc: **một người mở trình duyệt và đối chiếu bằng mắt**. Không
chạy crawler, không tải hàng loạt, không tự động hoá truy cập lên site đó — cả
vì site chặn, lẫn vì tín hiệu trong `robots.txt`.

Mọi asset nằm trong `web/public/` phải ghi được nguồn: tự sản xuất, mua bản
quyền, hoặc giấy phép mở có tên cụ thể.

## Alternatives Considered

1. **Sao chép nguyên trạng cả thương hiệu, chỉ dùng nội bộ để luyện tập.** Bị
   loại: repo này đang chứa một sản phẩm thật với luồng tiền thật, không phải
   bài tập; và ranh giới "chỉ nội bộ" không có cơ chế nào giữ được khi code đã
   nằm chung một cây thư mục.
2. **Không tham chiếu gì, tự thiết kế từ đầu.** Bị loại: phần lớn cấu trúc của
   một trang bán ô tô là quy ước chung của ngành; tự nghĩ lại từ đầu tốn công mà
   khách hàng Việt Nam lại thấy lạ.
3. **Chỉ mượn phong cách thị giác, IA tự định nghĩa.** Bị loại: IA là phần khó
   nhất và cũng là phần ít mang tính sở hữu nhất; bỏ đúng thứ nên mượn.

## Consequences

Positive:

- Sản phẩm mang thương hiệu IFast, triển khai công khai được, không phải gỡ bỏ.
- Nhóm web có một câu trả lời dứt khoát cho mọi tranh luận "lấy cái này được
  không".
- `web/public/` giữ được tính truy nguyên: mỗi file có một nguồn.

Tradeoffs:

- Phải tự sản xuất hoặc mua toàn bộ ảnh và nội dung marketing. Đây là câu hỏi
  mở Q1 trong [PRD](../product/web-prd.md) và nó chặn phần lớn công việc thị
  giác của giai đoạn P2.
- Việc xác minh cấu trúc là thủ công và không lặp lại tự động được, nên
  [sitemap](../product/web-sitemap.md) phải ghi rõ mục nào đã đối chiếu, mục nào
  còn là suy đoán.

## Follow-Up

- Trả lời Q1 trong PRD: nguồn ảnh và nội dung marketing.
- Bổ sung `web/public/SOURCES.md` ghi nguồn từng asset khi asset đầu tiên xuất hiện.
- Đối chiếu sitemap bằng trình duyệt ở bước 2 của [plan P2](../plans/active/p2-trai-nghiem-ban-xe-tren-web.md).
