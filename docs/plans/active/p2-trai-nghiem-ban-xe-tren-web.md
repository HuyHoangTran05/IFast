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
Chưa có asset và nội dung marketing chính thức, nên dùng placeholder trung tính
có kích thước đúng; không nhét ảnh mượn.
*Proof:* URL đã lọc dán sang tab mới ra đúng kết quả; số thẻ khớp số dòng xe API.

**5. Cấu hình và chi phí.** `/xe/[code]/cau-hinh` và `/xe/[code]/chi-phi`.
F-04, F-05, F-06, F-07, F-08.
*Proof:* cùng một dòng xe, Hà Nội và TP.HCM ra hai tổng khác nhau và khớp với
con số API trả về; đổi mốc thời gian thì lệ phí trước bạ đổi theo — dùng lại
đúng các con số đã ghi trong mục Validation của P1.

**6. Đặt cọc và tra cứu đơn.** F-10..F-14.
P2 cho phép đặt cọc không cần đăng nhập. Chính sách cọc là mock/config có nhãn
dữ liệu mẫu, sẵn sàng nhận contract backend; không hard-code thành chính sách
kinh doanh.
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
- **Asset và nội dung marketing chính thức chưa có.** P2 dùng placeholder trung
  tính theo quyết định Q1; mỗi asset thật sau này phải có nguồn truy nguyên theo
  decision 0002.
- **Chính sách cọc kinh doanh chưa chốt.** P2 chỉ dùng mock/config có nhãn dữ
  liệu mẫu và chờ contract backend; không biến mock thành chính sách quan sát
  được từ bên ngoài.
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

- [x] 1. Chạy `web` và `api` cùng lúc, xác nhận một lời gọi API thật
  - 2026-09-14: Dựng CPython 3.13.15 trong virtualenv cục bộ `py313`, nạp
    SQLite mẫu rồi chạy API tại `127.0.0.1:8000`. Web tại `127.0.0.1:3000`
    trả HTTP 200, có `VinFast VF 2`, và không có thông báo lỗi API; log API ghi
    `GET /catalog/models` 200 từ lần render Web.
  - Ghi chú môi trường cục bộ: Python 3.14/Mingw không cài được dependency có
    wheel native. Windows Application Control chặn SWC native của Next.js;
    phiên kiểm chứng dùng SWC WebAssembly và Webpack qua `npm.cmd run dev --
    --webpack` với biến `NEXT_TEST_WASM`/`NEXT_TEST_WASM_DIR`. Đây là workaround
    của máy hiện tại, không thay đổi cấu hình hay lệnh chuẩn của repo.
- [x] 2. Đối chiếu sitemap bằng trình duyệt, cập nhật `web-sitemap.md`
  - 2026-09-14: Người dùng đối chiếu thủ công homepage và link/CTA công khai
    tới detail VF 2, showroom/trạm sạc, bảo hành và FAQ/hỗ trợ; không dùng
    sitemap.xml, crawler hay tự động enumerate URL. Sitemap ghi nhận home là
    discovery surface, detail long-form, funnel đặt cọc stateful, showroom và
    hỗ trợ là destination riêng, cùng các giới hạn scope P2/P3/P4.
- [x] 3. Token, `SiteHeader`, `SiteFooter`, ba trạng thái
  - 2026-09-14: Thêm `globals.css` (token/reset/Inter), shell layout, header
    responsive có menu xe nhận từ Server Component, footer tĩnh, và ba state có
    thông báo cho screen reader. Style component dùng CSS Modules; không dùng
    asset hoặc nội dung từ VinFast.
  - `npm.cmd run typecheck` xanh. `npm.cmd run build -- --webpack` xanh với
    SWC WebAssembly workaround đã ghi ở bước 1; Next.js báo route `/` và
    `/xe/[code]` dynamic server-rendered.
  - Kiểm tương phản AA bằng công thức WCAG: `fg/bg` 16.82:1,
    `muted/surface` 6.40:1, `brand-fg/brand` 5.13:1, `inverse` 16.01:1,
    `accent/surface` 5.93:1, `warning/warning-bg` 6.21:1.
- [ ] 4. Trang chủ và `/xe` theo IA đã xác minh, dùng placeholder hợp lệ
- [ ] 5. `/xe/[code]/cau-hinh` và `/xe/[code]/chi-phi`
- [ ] 6. `/xe/[code]/dat-coc` và `/dat-coc/[maDon]` (cần contract backend cho cọc)
- [ ] 7. E2E luồng đặt cọc trong `tests/e2e/`
- [ ] 8. Lighthouse CI và axe trong CI (cần R4a)

Câu hỏi mở Q2, Q3 và Q6 nằm trong [PRD mục 9](../../product/web-prd.md). Các
quyết định Q1, Q4 và Q5 đã được ghi trong PRD mục 10; quyết định tương lai vẫn
phải được ghi vào PRD, không chỉ ghi ở đây.

## Decisions

- 2026-09-14: **Tách P2 khỏi P1 thay vì nối dài P1.** P1 là plan backend và đã
  đạt mục tiêu của nó ở mức API; gộp tiếp phần web sẽ tạo một file mà không ai
  đọc hết. P1 giữ nguyên vai trò nguồn sự thật cho backend; P2 nhận việc số 2 và
  số 3 trong danh sách còn lại của P1.
- 2026-09-14: **Xác minh IA bằng người, không bằng crawler.** Site tham chiếu
  chặn truy cập tự động và `robots.txt` từ chối dùng cho huấn luyện. Xem
  decision 0002.
- 2026-09-14: **Visual system tạm thời của IFast.** Dùng `#0B5FFF`, Inter,
  Lucide và placeholder trung tính; không sao chép asset hay nội dung từ site
  tham chiếu. Authority chi tiết: PRD mục 10, Q1.
- 2026-09-14: **Đặt cọc khách không cần đăng nhập ở P2.** Chính sách cọc chưa
  chốt dùng mock/config có nhãn dữ liệu mẫu, chờ contract backend thay vì
  hard-code. Authority chi tiết: PRD mục 10, Q4 và Q5.
- 2026-09-14: **IA P2 được xác minh thủ công từ reference.** Giữ URL tiếng Việt
  đã chốt của IFast; dùng reference để xác nhận discovery home, detail
  long-form, funnel đặt cọc stateful, CTA và vai trò riêng của showroom/hỗ trợ.
  Không suy ra sticky/mobile, không sao chép asset hay nội dung. Evidence ở
  `docs/product/web-sitemap.md`.
- 2026-09-14: **P2.3 dùng CSS custom properties + CSS Modules.** `globals.css`
  là token/reset/typography, mỗi component có CSS Module riêng; không thêm UI
  library. Inter đóng gói cục bộ, Lucide chỉ làm icon. Header lấy danh sách xe
  từ Server Component trước khi render và không gọi API khi mở menu; footer là
  dữ liệu tĩnh. Authority: `web-design-system.md` mục 2 và 3.

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
