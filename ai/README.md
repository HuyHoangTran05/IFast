# ai — Tính năng AI

Owner: **R3** (single owner).

Ranh giới cứng: `ai/` **chỉ nói chuyện với `api/`**, không bao giờ lộ trực tiếp
ra `web/`. Nhờ vậy R3 đổi prompt/model/provider tuỳ ý mà không đụng file của
role khác.

| Thư mục | Nội dung |
|---|---|
| `advisor/` | Tư vấn chọn xe theo nhu cầu, ngân sách, quãng đường đi hằng ngày |
| `compare/` | So sánh phiên bản, so sánh xe điện với xe xăng/dầu |
| `chat/` | Chatbot CSKH, hỏi đáp thông số và chính sách |
| `evals/` | Eval: độ chính xác thông số, tỉ lệ bịa số, chi phí, độ trễ |

## Luật không được vi phạm

Đây là sản phẩm bán xe — một câu trả lời sai về giá hoặc thông số là rủi ro
pháp lý, không phải lỗi UX.

- **Không bao giờ tự tính giá lăn bánh.** Gọi `api/pricing/`.
- **Không bao giờ đọc thông số từ trí nhớ model.** Gọi `api/catalog/`.
- **Không bao giờ tự suy ra khuyến mãi còn hiệu lực.** Gọi `api/promotions/`.
- Mỗi câu trả lời có số liệu phải dẫn được nguồn về bản ghi cụ thể.

Eval phải có một bộ test riêng cho đúng ba luật trên.
