# catalog — Dòng xe, phiên bản, thông số

Owner: **R2a**.

- Dòng xe và phiên bản (VF 2, VF 3, ...), bảng màu ngoại/nội thất, option.
- Thông số kỹ thuật **có cấu trúc**: công suất (kW), mô men xoắn (Nm), quãng
  đường NEDC (km), thời gian sạc nhanh, kiểu dẫn động, số chỗ.
- Brochure và tài sản media của từng dòng xe.

Thông số phải là dữ liệu có kiểu, không phải chuỗi tự do — `ai/` sẽ đọc từ đây
để trả lời, nên sai kiểu là sai câu trả lời cho khách.
