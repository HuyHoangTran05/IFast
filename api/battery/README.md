# battery — Pin và chính sách thuê pin

Owner: **R2a**. Đây là domain dễ làm sai nhất trong cả hệ thống.

Thuê pin không phải một tuỳ chọn giá — nó là **một hợp đồng tài sản có vòng
đời riêng**, tách khỏi vòng đời chiếc xe.

## Phải mô hình hoá được

- Pin là **tài sản có định danh** (serial), có trạng thái: đang cho thuê, đã
  trả, mất/thất lạc, hỏng không sửa được.
- **Chính sách bảo hành có phiên bản theo thời gian** — thời gian bảo hành áp
  dụng là chính sách tại *thời điểm hình thành tài sản*, không phải chính sách
  hiện hành.
- **Giá pin công bố thay đổi theo thời gian** — khi tính bồi thường phải lấy
  giá tại *thời điểm xảy ra sự cố*.

## Công thức bồi thường pin thuê

    B = A × (1 − T1 / T2)

- `B` — giá trị bồi thường
- `A` — giá pin công bố **tại thời điểm xảy ra sự cố**
- `T1` — thời gian sử dụng, tính tròn theo tháng: **từ 15 ngày tính tròn lên**,
  dưới 15 ngày tính tròn xuống
- `T2` — thời gian bảo hành theo chính sách **tại thời điểm hình thành tài sản**

Ràng buộc: **`B` không bao giờ thấp hơn 10% của `A`.**

Ba cái bẫy trong đúng một công thức này:

1. Hai lần tra chính sách ở **hai mốc thời gian khác nhau** — lấy nhầm chính
   sách hiện hành là tính sai tiền của khách.
2. Luật làm tròn 15 ngày — làm tròn sai là lệch nguyên một tháng tiền.
3. Sàn 10% — thiếu ràng buộc này thì pin gần hết bảo hành sẽ ra bồi thường ~0.

Trường hợp pin sửa được thì không dùng công thức: thanh toán theo báo giá thực
tế của xưởng dịch vụ.

## Ranh giới

Domain này giữ **chính sách và cách tính**. Việc thu tiền định kỳ của thuê bao
thuê pin thuộc `payments/` (R2b). Đừng tự dựng billing ở đây.
