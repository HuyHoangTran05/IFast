# Prompt: dựng trải nghiệm web bán xe (plan mode)

Dùng cho giai đoạn P2 trong [plan P2](../plans/active/p2-trai-nghiem-ban-xe-tren-web.md).
Bật plan mode rồi dán khối dưới đây.

Prompt này cố tình **không** mô tả lại yêu cầu. Yêu cầu nằm trong PRD; chép lại
vào prompt chỉ tạo ra một bản sao sẽ lệch sau vài ngày.

---

## Bản đầy đủ — dùng khi bắt đầu một đợt làm việc

```text
Mục tiêu: đưa web IFast tới trạng thái khách hàng đi được trọn vẹn từ trang chủ
đến mã đơn đặt cọc, với mọi con số tiền khớp API và không đổi sau khi đơn đã chốt.

Đọc trước, theo đúng thứ tự này, và đừng đọc rộng hơn mức cần:
1. AGENTS.md và docs/WORKFLOW.md — cách làm việc trong repo này.
2. docs/plans/active/p2-trai-nghiem-ban-xe-tren-web.md — thứ tự thực thi và
   trạng thái hiện tại. Đây là nguồn sự thật cho việc cần làm.
3. docs/product/web-prd.md — hành vi phải đạt, mục 5 và mục 6.
4. docs/product/web-sitemap.md — trang nào, dữ liệu lấy từ module api/ nào.
5. docs/product/web-design-system.md — token và component.
6. docs/decisions/0002-ranh-gioi-tham-chieu-giao-dien.md — được tham chiếu
   vinfastauto.com tới đâu.
7. docs/RUNBOOK.md — cách chạy api/ và web/ cùng lúc.

Làm bước chưa tick tiếp theo trong mục Progress của plan P2. Không nhảy cóc:
mỗi bước là điều kiện của bước sau.

Ranh giới không được vượt:
- Không sao chép logo, nhãn hiệu, tên dòng xe, ảnh, video, font, văn bản, hay
  CSS từ vinfastauto.com. Chỉ tham chiếu cấu trúc. Không chạy crawler lên site đó.
- Không tính tiền ở client. web/src/lib/money.ts chỉ định dạng. Mọi phép tính ở api/.
- Không ghép tổng ở client từ nhiều lời gọi API. Tổng do API trả về.
- Không khai báo tay type cho phản hồi API. Sinh bằng: cd web && npm run gen:api
- Không dựng trang chưa có nguồn dữ liệu bằng nội dung cứng trong code.
- Không đụng vào api/ trừ khi plan P2 ghi rõ. Nếu cần backend đổi, dừng và nói.
- Không đụng vào .github/workflows/ nếu chưa có R4a đồng ý.

Dừng lại và hỏi, đừng tự chọn mặc định, nếu chạm phải câu hỏi mở nào trong
docs/product/web-prd.md mục 9 mà chưa có câu trả lời trong chính tài liệu đó.
Cụ thể: Q1 chặn trang chủ và trang danh mục; Q4 và Q5 chặn trang đặt cọc.
Mặc định cấu hình được không phải là authority.

Ghi kết quả vào đâu:
- Tiến độ và quyết định cục bộ: cập nhật docs/plans/active/p2-trai-nghiem-ban-xe-tren-web.md.
- Hành vi đổi: sửa docs/product/web-prd.md trước khi sửa code.
- Quyết định sản phẩm hoặc kiến trúc phải kế thừa lâu dài: thêm file vào docs/decisions/.
- Không tạo file plan hay file trạng thái song song ở nơi khác.

Chứng cứ bắt buộc trước khi nói xong bất cứ điều gì:
- cd web && npm run typecheck && npm run build
- Với bước có liên quan tới tiền: một lời gọi API thật và con số hiển thị khớp
  phản hồi API, dán cả hai vào báo cáo.
- Với bước 7: test E2E chạy và xanh, dán output.
Không có chứng cứ thì báo cáo là chưa chứng minh, đừng báo cáo là xong.

Kết thúc bằng: kết quả · file đã đổi · lệnh đã chạy và kết quả thật · rủi ro còn lại.
```

## Bản ngắn — dùng cho một bước lẻ

```text
Làm bước <N> trong docs/plans/active/p2-trai-nghiem-ban-xe-tren-web.md.

Đọc: plan P2 (mục Approach, bước <N>), và phần PRD mà bước đó viện dẫn
(docs/product/web-prd.md). Đọc docs/product/web-design-system.md nếu bước đó
dựng component.

Giữ nguyên các ranh giới của repo: không tính tiền ở client, không sao chép tài
sản thị giác từ site tham chiếu, type API sinh từ contract.

Nếu bước này chạm câu hỏi mở chưa trả lời trong PRD mục 9 thì dừng và hỏi.

Xong thì tick vào Progress của plan P2, và báo cáo kèm output thật của
cd web && npm run typecheck && npm run build.
```

## Bản dùng cho việc rà soát, không sửa

```text
Chỉ đọc, không sửa file nào.

Đối chiếu docs/product/web-sitemap.md với thực tế:
- Cột "Nguồn dữ liệu": mỗi module nhắc tới có thật trong api/ không, và có phải
  stub không. Kiểm bằng ls api/ và grep include_router api/main.py.
- Cột "Trạng thái": đối chiếu với file thật trong web/src/app/.

Báo cáo từng dòng lệch, kèm file:line làm chứng. Đừng sửa gì — đề xuất diff thôi.
```
