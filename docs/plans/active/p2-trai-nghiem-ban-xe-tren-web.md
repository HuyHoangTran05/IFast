# Execution Plan: P2 — Trải nghiệm bán xe trên web

Date: 2026-09-14

## Status

Active

## Outcome

Khách hàng trên điện thoại đi được trọn vẹn từ trang chủ đến mã đơn đặt cọc mà
không cần gọi ai: tìm xe → chọn cấu hình và mô hình sở hữu → thấy chi phí lăn
bánh tại tỉnh của mình kèm ưu đãi còn hiệu lực → đặt cọc → mở lại đơn thấy đúng
con số hôm đặt, kể cả sau khi bảng giá đã đổi.

Chứng cứ hoàn tất: E2E luồng đặt cọc xanh trong CI, gồm kịch bản tăng giá sau
khi chốt đơn.

## Context

- Hành vi phải đạt: [PRD](../../product/web-prd.md) — F-01..F-14, N-01..N-09.
- Trang nào, dữ liệu từ đâu: [sitemap](../../product/web-sitemap.md).
- Trang trông thế nào: [ngôn ngữ thiết kế](../../product/web-design-system.md).
- Được tham chiếu site ngoài tới đâu:
  [decision 0002](../../decisions/0002-ranh-gioi-tham-chieu-giao-dien.md).
- Backend đã có gì: [plan P1](p1-nen-tang-ban-xe.md). P2 nhận việc số 2 và số 3
  trong danh sách còn lại của P1.
- Phân vai: [decision 0001](../../decisions/0001-team-roles-and-ownership-boundaries.md).
  P2 chủ yếu là R1; bước 7 là R4b; bước 8 cần R4a.
- Cách chạy: [RUNBOOK](../../RUNBOOK.md).
- Contract: `contracts/openapi.yaml`, type sinh bằng `cd web && npm run gen:api`.

## Scope

In scope:

- Bảy tuyến đường P2 trong sitemap: `/`, `/xe`, `/xe/[code]`,
  `/xe/[code]/cau-hinh`, `/xe/[code]/chi-phi`, `/xe/[code]/dat-coc`,
  `/dat-coc/[maDon]`.
- Token thiết kế và 14 component trong bảng của tài liệu ngôn ngữ thiết kế.
- E2E luồng đặt cọc trong `tests/e2e/`.
- Lighthouse CI và axe trong CI, nếu R4a đồng ý.

Out of scope (thuộc P3, P4, hoặc chưa có authority):

- Lái thử, đăng nhập, tài khoản, dịch vụ pin, so sánh xe — giai đoạn P3, và các
  module `api/` tương ứng hiện mới là stub.
- Đại lý, trạm sạc, tin tức, chính sách, hỗ trợ — giai đoạn P4, chưa có nguồn
  nội dung.
- Cổng thanh toán thật — cần decision riêng, theo P1 mục 7.
- Tiếng Anh. Kiến trúc phải cho phép thêm sau, nhưng không dựng ở P2 (N-05).

## Approach

Thứ tự dưới đây không đổi chỗ được: mỗi bước là điều kiện của bước sau.

**1. Chạy `web` và `api` cùng lúc.** Đây là việc số 1 đang treo của P1 và mọi
thứ khác đều giả định nó đúng. Không viết component nào trước khi một lời gọi
API thật từ trình duyệt trả về dữ liệu thật.
*Proof:* ảnh chụp hoặc log cho thấy `/xe` render danh sách xe từ `api/catalog`
đang chạy, không phải dữ liệu giả.

**2. Đối chiếu sitemap bằng trình duyệt.** Một người mở site tham chiếu, đối
chiếu bảng tuyến đường, và sửa `web-sitemap.md`. Site đó chặn truy cập tự động
nên không có cách nào khác; decision 0002 cấm crawl.
*Proof:* diff trên `web-sitemap.md` và không còn dòng nào ở trạng thái suy đoán
trong nhóm P2.

**3. Token và khung layout.** `globals.css` với token, `SiteHeader`,
`SiteFooter`, ba trạng thái Loading/Error/Empty. Chốt luôn chuyện dùng CSS
Modules hay thư viện, và ghi quyết định vào mục Decisions của file này.
*Proof:* `npm run typecheck && npm run build` xanh; kiểm tương phản màu đạt AA.

**4. Trang chủ và làm lại `/xe`.** Theo IA đã xác minh ở bước 2. F-01, F-02.
*Chặn bởi Q1* — nếu chưa có nguồn ảnh và nội dung marketing thì dựng bố cục với
chỗ trống có kích thước đúng, không nhét ảnh mượn.
*Proof:* URL đã lọc dán sang tab mới ra đúng kết quả; số thẻ khớp số dòng xe API.

**5. Cấu hình và chi phí.** `/xe/[code]/cau-hinh` và `/xe/[code]/chi-phi`.
F-04, F-05, F-06, F-07, F-08.
*Proof:* cùng một dòng xe, Hà Nội và TP.HCM ra hai tổng khác nhau và khớp với
con số API trả về; đổi mốc thời gian thì lệ phí trước bạ đổi theo — dùng lại
đúng các con số đã ghi trong mục Validation của P1.

**6. Đặt cọc và tra cứu đơn.** F-10..F-14.
*Chặn bởi Q4 và Q5* — chính sách tiền cọc và việc có bắt đăng nhập hay không.
Không tự chọn mặc định; dừng và hỏi.
*Proof:* gửi trùng không tạo đơn thứ hai; lỗi server hiện đúng trường.

**7. E2E trong `tests/e2e/`.** Việc số 3 của P1. Kịch bản bắt buộc: đặt đơn →
tăng giá trong `api/pricing` → mở lại trang đơn → con số không đổi, trong khi
báo giá trên trang xe thì đổi.
*Proof:* test xanh trong CI.

**8. Lighthouse CI và axe.** Thêm vào `.github/workflows/ci.yml`. Cần R4a đồng ý
trước vì đụng vào CI.
*Proof:* CI chạy và báo số đo thật cho ba tuyến đường; N-01 và N-03 có ngưỡng.

## Risks And Recovery

- **Bước 1 có thể lộ ra contract đúng trên giấy nhưng sai khi chạy.** Đó chính
  là lý do nó đứng đầu. Nếu lệch: sinh lại type bằng `npm run gen:api` và chạy
  `python scripts/generate-contract.py --check` để xác định bên nào lệch.
- **Q1 chặn phần lớn công việc thị giác.** Giảm thiểu: bước 3, 5, 6, 7 không phụ
  thuộc Q1, nên vẫn chạy được song song trong khi chờ. Chỉ bước 4 phải chờ.
- **Q4 và Q5 chặn bước 6.** Đây là stop condition thật, không phải rủi ro mềm:
  tiền cọc và điều kiện đăng nhập là chính sách quan sát được từ bên ngoài, mặc
  định cấu hình được không phải authority. Dừng trước khi viết code trang đặt cọc.
- **Dữ liệu biểu phí vẫn là dữ liệu mẫu.** Kế thừa rủi ro của P1. F-07 bắt giao
  diện phải hiện cảnh báo, nên rủi ro "ai đó tưởng là số thật" được chặn ở tầng
  giao diện, nhưng vẫn **phải thay trước khi lên production**.
- **Cám dỗ tính tiền ở client cho nhanh.** Mỗi lần đổi lựa chọn mà gọi lại API
  thì chậm hơn tính tại chỗ. Không đánh đổi: luật 1 mục 4 của tài liệu thiết kế.
  Cách chống: cơ chế hoá bằng kiểm tra máy móc, không dựa vào review.
- **Recovery:** web không giữ trạng thái máy chủ nào.
  `rm -f ifast.db && python scripts/seed-dev.py` đưa backend về sạch.
  Mọi thay đổi của P2 nằm trong `web/` và `tests/e2e/`, hoàn tác bằng git.

## Progress

- [ ] 1. Chạy `web` và `api` cùng lúc, xác nhận một lời gọi API thật
- [ ] 2. Đối chiếu sitemap bằng trình duyệt, cập nhật `web-sitemap.md`
- [ ] 3. Token, `SiteHeader`, `SiteFooter`, ba trạng thái
- [ ] 4. Trang chủ và `/xe` theo IA đã xác minh (chặn bởi Q1)
- [ ] 5. `/xe/[code]/cau-hinh` và `/xe/[code]/chi-phi`
- [ ] 6. `/xe/[code]/dat-coc` và `/dat-coc/[maDon]` (chặn bởi Q4, Q5)
- [ ] 7. E2E luồng đặt cọc trong `tests/e2e/`
- [ ] 8. Lighthouse CI và axe trong CI (cần R4a)

Câu hỏi mở Q1..Q6 nằm trong [PRD mục 9](../../product/web-prd.md). Trả lời câu
nào thì ghi câu trả lời vào PRD, không ghi vào đây.

## Decisions

- 2026-09-14: **Tách P2 khỏi P1 thay vì nối dài P1.** P1 là plan backend và đã
  đạt mục tiêu của nó ở mức API; gộp tiếp phần web sẽ tạo một file mà không ai
  đọc hết. P1 giữ nguyên vai trò nguồn sự thật cho backend; P2 nhận việc số 2 và
  số 3 trong danh sách còn lại của P1.
- 2026-09-14: **Xác minh IA bằng người, không bằng crawler.** Site tham chiếu
  chặn truy cập tự động và `robots.txt` từ chối dùng cho huấn luyện. Xem
  decision 0002.

Quyết định lâu dài về sản phẩm hoặc kiến trúc thì chuyển lên `docs/decisions/`.

## Validation

- Focused proof: `cd web && npm run typecheck && npm run build`.
- Integration proof: web gọi API thật đang chạy, đối chiếu con số hiển thị với
  phản hồi API cho cùng tổ hợp dòng xe, tỉnh, và mốc thời gian.
- End-to-end proof: `tests/e2e/` luồng đặt cọc, gồm kịch bản giá đổi sau khi
  chốt đơn.
- Repository-required checks: `python -m pytest`,
  `python scripts/generate-contract.py --check`, `ruff check`,
  `ruff format --check`, và bộ lệnh web ở trên. Toàn bộ nằm trong
  `.github/workflows/ci.yml`.

## Result

Chưa hoàn tất. Hoàn tất khi F-01..F-14 đạt tiêu chí chấp nhận trong PRD, N-01
đến N-09 có số đo, E2E xanh trong CI, và sitemap không còn tuyến đường nào ở
trạng thái suy đoán. Khi đó chuyển file này sang `docs/plans/completed/`.
