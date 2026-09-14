# pricing — Giá và dự toán chi phí lăn bánh

Owner: **R2a**. Đây là module nhiều nghiệp vụ nhất của R2a.

- **Biến thể giá**: kèm pin vs thuê pin — hai mô hình sở hữu khác nhau, không
  phải một field boolean.
- **Giá niêm yết vs giá ưu đãi**: giá ưu đãi đến từ `promotions/`, không hard-code.
- **Dự toán lăn bánh**: phí trước bạ, phí đăng ký biển số, phí đường bộ, bảo
  hiểm. Các khoản này **khác nhau theo tỉnh/thành**, nên cần bảng tham số theo
  địa phương có hiệu lực theo thời gian.
- **So sánh chi phí vận hành** với xe xăng/dầu: cần giá nhiên liệu theo vùng,
  cập nhật định kỳ và có ngày hiệu lực.

Luật: mọi con số ở đây là **tính toán xác định**, không phải ước lượng. `ai/`
không được tự tính — phải gọi module này.
