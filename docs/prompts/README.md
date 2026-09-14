# Prompt dùng lại được

Thư mục này chứa prompt đã soạn sẵn cho những việc lặp lại nhiều phiên. Prompt
ở đây **không phải** tài liệu sản phẩm: chúng chỉ trỏ tới tài liệu sản phẩm.
Khi hành vi đổi, sửa `docs/product/` và `docs/plans/`, không sửa prompt.

Cách dùng: mở prompt, sao chép phần trong khối, dán vào phiên làm việc. Với
Claude Code thì bật plan mode trước khi dán nếu prompt ghi rõ như vậy.

## Danh mục

| Prompt | Dùng khi nào | Chế độ |
| --- | --- | --- |
| [clone-web-plan-mode.md](clone-web-plan-mode.md) | Bắt đầu hoặc tiếp tục giai đoạn P2 của web | Plan mode |

## Quy tắc viết prompt trong repo này

1. Prompt nêu **kết quả mong muốn**, không nêu các bước chi tiết — các bước nằm
   trong plan.
2. Prompt liệt kê **tài liệu bắt buộc đọc trước**, đường dẫn tương đối từ gốc repo.
3. Prompt nêu **ranh giới không được vượt** và **điều kiện dừng**.
4. Prompt nói rõ **kết quả đổ vào file nào**, để không sinh ra tài liệu song song.
5. Prompt không nhắc lại nội dung tài liệu. Nhắc lại là tạo ra bản sao sẽ lệch.
