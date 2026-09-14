# PRD — Backend IFast

Ngày: 2026-09-14 · Trạng thái: Mô tả hiện trạng + yêu cầu cho phần chưa làm
Chủ sở hữu: R2a (sản phẩm và giá), R2b (khách hàng và giao dịch)

Tài liệu này tách **yêu cầu** khỏi **hiện thực**. Quy tắc nghiệp vụ hiện sống
trong docstring của code; ở đây chúng được phát biểu thành yêu cầu kiểm chứng
được, mỗi yêu cầu trỏ tới test đang chứng minh nó.

Liên quan: [ARCHITECTURE.md](../ARCHITECTURE.md) · [mô hình dữ liệu](data-model.md)
· [quy ước API](api-conventions.md) · [từ điển thuật ngữ](glossary.md)
· [PRD web](web-prd.md) · [plan P1](../plans/active/p1-nen-tang-ban-xe.md).

## 1. Sản phẩm này phải làm đúng điều gì

Bán một chiếc ô tô điện ở Việt Nam. Nghĩa là: trả lời đúng câu hỏi "chiếc xe này
tốn của tôi bao nhiêu tiền, tại tỉnh của tôi, hôm nay", rồi giữ nguyên câu trả
lời đó sau khi khách đã xuống tiền.

Sai một con số tiền trên trang bán xe là rủi ro pháp lý, không phải lỗi hiển thị.
Mọi yêu cầu dưới đây đều phục vụ mệnh đề đó.

## 2. Trạng thái từng domain

| Domain | Chủ | Trạng thái | Endpoint |
| --- | --- | --- | --- |
| `catalog` | R2a | Chạy được | `/catalog/models`, `/catalog/models/{code}` |
| `pricing` | R2a | Chạy được | `/pricing/on-road`, `/pricing/running-cost` |
| `promotions` | R2a | Chạy được | `/promotions` |
| `battery` | R2a | Chạy được | `/battery/assets/{serial}/compensation` |
| `orders` | R2b | Chạy được | `POST /orders`, `/orders/{code}` |
| `inventory` | R2a | **Stub** — chỉ có README | — |
| `dealers` | R2a | **Stub** | — |
| `auth` | R2b | **Stub** | — |
| `users` | R2b | **Stub** | — |
| `testdrive` | R2b | **Stub** | — |
| `payments` | R2b | **Stub** | — |
| `notifications` | R2b | **Stub** | — |

## 3. Yêu cầu nền tảng — áp cho mọi domain

**B-01 — Tiền là số nguyên đồng.** Không `float` cho tiền ở bất kỳ đâu. Tỉ lệ
dùng `Decimal`, quy về số nguyên một lần duy nhất ở bước cuối, làm tròn nửa lên.
*Hiện thực:* `api/core/money.py`.
*Chấp nhận:* không có annotation `float` nào cho một đại lượng tiền trong `api/`.

**B-02 — Ngày nghiệp vụ theo giờ Việt Nam.** "Hôm nay" là hôm nay ở Việt Nam,
không phải ở máy chủ.
*Hiện thực:* `api/core/clock.py`, `BUSINESS_TIMEZONE = Asia/Ho_Chi_Minh`.
*Chấp nhận:* máy chủ chạy UTC lúc 23 giờ giờ Việt Nam vẫn ghi đúng ngày hôm đó;
một ưu đãi bắt đầu ngày 10/02 có hiệu lực từ 0 giờ ngày 10/02 giờ Việt Nam.

**B-03 — Mọi chính sách có khoảng hiệu lực, mọi phép tính nhận `as_of`.** Không
hàm tính tiền nào được mặc định về "hiện tại" bên trong.
*Hiện thực:* `api/core/effective.py`; mọi hàm trong `api/pricing/service.py`,
`api/promotions/service.py`, `api/battery/service.py` đều nhận `as_of`.
*Chấp nhận:* `api/tests/test_api.py::test_bieu_phi_2027_lam_tong_tang` — cùng
tỉnh, hai mốc thời gian, hai tổng khác nhau.

**B-04 — Thiếu dữ liệu thì báo lỗi, không mặc định về 0.** Một tỉnh chưa có biểu
phí phải trả "chưa hỗ trợ", không được trả chi phí lăn bánh bằng đúng giá xe.
*Hiện thực:* `latest_effective_on()` trả `None`; `PricingUnavailable`,
`BatteryPolicyUnavailable`; router ánh xạ sang 404.
*Chấp nhận:*
`api/tests/test_api.py::test_tinh_chua_ho_tro_tra_404_chu_khong_tra_gia_bang_gia_xe`.

**B-05 — Kết quả tất định.** Cùng dữ liệu vào, cùng `as_of`, luôn ra cùng kết
quả — kể cả khi nhiều bản ghi cùng hợp lệ.
*Hiện thực:* luật ưu tiên ưu đãi có tie-break tới tận mã ưu đãi
(`api/promotions/service.py::_reverse_code`).
*Chấp nhận:* `api/tests/test_promotions.py::TestLuatUuTien`.

## 4. Catalog — bán cái gì

**B-10 — Thông số kỹ thuật có kiểu dữ liệu.** Mỗi đại lượng một cột có kiểu và
đơn vị rõ ràng. Không bao giờ nhét thông số vào một cột văn bản tự do.
*Lý do:* `ai/` đọc trực tiếp schema này để trả lời khách; một chuỗi tự do buộc
mô hình phải diễn giải, và diễn giải sai một con số về xe là rủi ro pháp lý.
*Hiện thực:* `api/catalog/models.py::Spec`, 10 cột có kiểu.
*Chấp nhận:* `api/tests/test_api.py::test_lay_thong_so_vf2_dung_kieu_du_lieu`.

**B-11 — Nhiều loại sản phẩm có tập thông số khác nhau.** Ô tô đo bằng kW và km
NEDC; xe máy điện đo bằng W và km mỗi lần sạc.
*Hiện thực:* `ProductCategory` (car, motorbike); các cột thông số cho phép NULL.
*Ghi chú:* xe máy điện **ngoài phạm vi giai đoạn đầu**, nhưng schema đã chừa
đường vì thêm loại sản phẩm sau khi đã có dữ liệu thật thì rất đắt.

**B-12 — Giá gắn với phiên bản, không gắn với dòng xe.**
*Hiện thực:* `PriceBookEntry.trim_id` trỏ tới `catalog_trim`.

**B-13 — Dòng xe không tồn tại trả 404.**
*Chấp nhận:* `api/tests/test_api.py::test_dong_xe_khong_ton_tai_tra_404`.

## 5. Pricing — giá bao nhiêu

**B-20 — Hai mô hình sở hữu là hai biến thể giá, không phải một cờ.** Kèm pin và
thuê pin cho hai con số khác nhau; thuê pin còn có phí hằng tháng.
*Hiện thực:* `OwnershipModel`, `PriceBookEntry.monthly_battery_fee_vnd`.
*Chấp nhận:*
`api/tests/test_api.py::test_thue_pin_ra_gia_khac_va_co_phi_hang_thang`.

**B-21 — Chi phí lăn bánh khoá theo tỉnh.** Cùng một chiếc xe, hai tỉnh, hai con
số — lệ phí trước bạ và phí biển số khác nhau giữa các tỉnh.
*Hiện thực:* `RegistrationFeeSchedule.province_code`.
*Chấp nhận:* `api/tests/test_api.py::test_cung_xe_khac_tinh_ra_tong_khac`. Số đo
đã ghi trong plan P1: Hà Nội 202.980.700 so với TP.HCM 193.980.700 cùng ngày.

**B-22 — Dự toán luôn kèm phần tách khoản.** Khách nhìn tổng, nhưng khi thắc mắc
phải giải thích được từng khoản. Bảy khoản: giá xe, lệ phí trước bạ, phí biển số,
phí đăng kiểm, phí đường bộ một năm, bảo hiểm TNDS bắt buộc, phí dịch vụ đăng ký.
*Hiện thực:* `OnRoadQuote.items`.
*Chấp nhận:* `api/tests/test_api.py::test_du_toan_lan_banh_ha_noi`.

**B-23 — Lệ phí trước bạ tính trên giá sau khi trừ ưu đãi.** Tính trên giá niêm
yết khiến khách phải trả nhiều hơn thực tế.
*Hiện thực:* `quote_on_road_cost()` nhận `discount_vnd` và trừ trước khi nhân tỉ
lệ. Thứ tự này không đổi chỗ được.
*Chấp nhận:* `api/tests/test_pricing.py::TestOnRoadCost`.

**B-24 — Ưu đãi không được âm và không được vượt quá giá xe.**
*Hiện thực:* `quote_on_road_cost()` ném `ValueError`, router trả 422.

**B-25 — So sánh chi phí vận hành dẫn được ngày của giá đã dùng.** Giá điện và
giá nhiên liệu là dữ liệu có mốc thời gian, không phải hằng số.
*Hiện thực:* `RunningCostComparison.electricity_price_as_of`, `.fuel_price_as_of`.
*Chấp nhận:* `api/tests/test_api.py::test_so_sanh_chi_phi_dan_duoc_ngay_cua_gia`.

**B-26 — Mức tiêu thụ nhận vào dưới dạng nhân 10.** Tránh `float` cho dữ liệu
người dùng nhập. 6,5 lít/100km truyền vào là `65`.

## 6. Promotions — ưu đãi

**B-30 — Ưu đãi là thực thể có vòng đời, không phải một cột giảm giá.** Có mốc
bắt đầu, có thể có mốc kết thúc, có điều kiện áp dụng, và nhiều ưu đãi tồn tại
cùng lúc là chuyện bình thường.
*Hiện thực:* `promotions_promotion` với `effective_from`/`effective_to`,
`trim_id`, `province_code`, `ownership_model`, `priority`, `stackable`.

**B-31 — Ba loại ưu đãi.** Số tiền cố định, phần trăm giá, và hiện vật.
*Hiện thực:* `PromotionKind`.

**B-32 — Luật ưu tiên, đúng bốn bước.**
1. Loại ưu đãi hết hiệu lực tại `as_of` và ưu đãi không khớp điều kiện.
2. Chia phần còn lại thành nhóm cộng dồn được và nhóm không cộng dồn.
3. Phương án A là ưu đãi không cộng dồn tốt nhất, đứng **một mình**. Phương án B
   là tổng toàn bộ ưu đãi cộng dồn được.
4. Chọn phương án có lợi hơn cho khách. Bằng nhau thì chọn A.

"Tốt nhất" ở bước 3: ưu tiên cao hơn trước, rồi số tiền giảm lớn hơn, rồi mã ưu
đãi theo thứ tự chữ cái.
*Hiện thực:* `api/promotions/service.py::resolve_promotions`.
*Chấp nhận:* `api/tests/test_promotions.py::TestLuatUuTien`, `TestHieuLuc`,
`TestDieuKien`.

**B-33 — Ưu đãi hiện vật vẫn được liệt kê dù giảm 0 đồng.** Khách cần thấy nó và
nó vẫn kèm điều khoản riêng.

**B-34 — Ưu đãi chưa tới ngày bắt đầu không được áp.**
*Chấp nhận:*
`api/tests/test_api.py::test_uu_dai_mien_phi_sac_chua_chay_truoc_10_02_2026`.

## 7. Battery — pin thuê

**B-40 — Công thức bồi thường.** `B = A × (1 − T1/T2)`, trong đó `A` là giá pin
công bố, `T1` thời gian sử dụng tính tròn theo tháng, `T2` thời gian bảo hành.

**B-41 — `A` và `T2` tra ở hai mốc thời gian khác nhau.** `A` tại thời điểm xảy
ra sự cố; `T2` theo chính sách tại thời điểm hình thành tài sản. Dùng chính sách
hiện hành cho cả hai là tính sai tiền của khách.
*Hiện thực:* `compute_compensation()` gọi `latest_effective_on` hai lần với hai
mốc khác nhau.

**B-42 — Luật làm tròn 15 ngày.** Phần dư từ 15 ngày trở lên tính thêm một tháng,
dưới 15 ngày bỏ. Làm tròn sai lệch nguyên một tháng khấu hao.
*Hiện thực:* `months_of_use()`, `ROUND_UP_FROM_DAYS = 15`. Cộng tháng có kẹp về
ngày cuối tháng: 31/01 cộng một tháng ra 28/02, không tràn sang tháng 3.
*Chấp nhận:* `api/tests/test_battery_compensation.py::TestMonthRounding`.

**B-43 — Sàn 10% giá công bố.** Thiếu nó thì pin gần hết bảo hành ra bồi thường
gần bằng không, và pin quá hạn bảo hành ra số âm.
*Hiện thực:* `MINIMUM_COMPENSATION_RATE = Decimal("0.10")`, cờ `floor_applied`.
*Chấp nhận:* `api/tests/test_battery_compensation.py::TestCompensation`. Số đo
trong plan P1: sau 24 tháng ra 67.500.000; sau 94 tháng chạm sàn 9.000.000.

**B-44 — Kết quả trả kèm toàn bộ căn cứ.** Đây là số tiền đòi khách trả, nên phải
giải thích được: giá nào, ngày nào, chính sách nào, có bị chặn bởi sàn không.
*Hiện thực:* `CompensationBreakdown`.

**B-45 — Pin còn sửa được thì không dùng công thức này.** Thanh toán theo báo giá
thực tế của xưởng dịch vụ. Hiện chưa có đường đi nào trong code cho trường hợp
này — là khoảng trống có chủ ý, không phải thiếu sót bị bỏ quên.

## 8. Orders — đặt cọc

**B-50 — Đơn chốt xong là đóng băng.** Toàn bộ giá, ưu đãi và cấu hình được chụp
vào chính đơn; sau đó đơn không đọc lại bảng giá.
*Hiện thực:* `orders_order.price_snapshot`, `build_snapshot()`.
*Chấp nhận:*
`api/tests/test_orders_snapshot.py::test_bang_gia_doi_sau_khong_lam_doi_don_da_chot`
và `test_uu_dai_het_han_sau_do_khong_bi_go_khoi_don`. Số đo trong plan P1: sau
khi tăng giá lên 220 triệu, báo giá mới ra 234.980.700 còn đơn đã chốt vẫn giữ
202.980.700.

**B-51 — Snapshot đủ để giải thích lại sau nhiều năm.** Gồm `as_of`, tỉnh, mô
hình sở hữu, giá xe, tổng giảm, phí pin hằng tháng, bảy khoản tách, tổng, và danh
sách ưu đãi đã áp.
*Chấp nhận:*
`api/tests/test_orders_snapshot.py::test_snapshot_giu_du_can_cu_de_giai_thich_lai`.

**B-52 — Hai luồng mua, không ép chung một máy trạng thái.** Ô tô đi qua đặt cọc
rồi hợp đồng rồi giao xe; xe máy và phụ kiện mua thẳng.
*Hiện thực:* `OrderChannel` (deposit, direct_purchase).

**B-53 — Sáu trạng thái đơn.** draft, deposit_pending, deposit_paid,
contract_signed, delivered, cancelled. Đơn mới tạo ở `deposit_pending`.
*Chấp nhận:* `api/tests/test_orders_snapshot.py::test_don_moi_tao_cho_thanh_toan_coc`.
*Khoảng trống:* **chưa có API chuyển trạng thái.** Không có đường nào để đánh dấu
đã thanh toán cọc hay đã ký hợp đồng. Cần `payments` trước.

**B-54 — Tiền cọc không âm và không vượt quá tổng giá trị đơn.**
*Chấp nhận:* `api/tests/test_api.py::test_tien_coc_lon_hon_gia_tri_don_bi_tu_choi`.

**B-55 — Snapshot không bao giờ bị ghi đè sau khi rời trạng thái nháp.**
*Hiện thực:* `assert_snapshot_intact()` ném `OrderImmutable`.
*Khoảng trống:* hàm này tồn tại nhưng **chưa được gọi ở đường đi nào trong
router**. Bất biến hiện được giữ bằng việc không có endpoint nào sửa đơn, chứ
không phải bằng một kiểm tra chủ động.

## 9. Ranh giới với `ai/`

**B-60 — `ai/` không tự tính tiền.** Mọi con số đi qua `api/`.
*Chấp nhận:* `ai/evals/test_guardrails.py::test_khong_cong_cu_nao_tu_tinh_tien`
quét mã nguồn của registry công cụ.

**B-61 — Mọi kết quả công cụ mang theo nguồn và mốc thời gian.**
*Chấp nhận:* `ai/evals/test_guardrails.py::test_moi_ket_qua_deu_mang_theo_nguon`.

**B-62 — Không có dữ liệu thì nói không biết, không ước lượng.**
*Chấp nhận:* `test_tinh_chua_co_bieu_phi_thi_bao_khong_biet_chu_khong_uoc_luong`,
`test_hoi_dong_xe_khong_ton_tai_thi_bao_khong_biet`.

**B-63 — Chưa cấu hình mô hình thì từ chối, không bịa.**
*Chấp nhận:* `ai/evals/test_guardrails.py::test_chua_cau_hinh_model_thi_tu_choi_chu_khong_bia`.

## 10. Yêu cầu cho bảy module còn là stub

Mỗi mục dưới đây đủ để bắt tay viết, nhưng **chưa mục nào được mở** cho tới khi
câu hỏi mở tương ứng ở mục 12 có câu trả lời.

Thứ tự phụ thuộc: `dealers` là dữ liệu nền cho `testdrive`, `inventory` và
`orders` (nhận xe ở đâu). `auth` và `users` là nền cho `payments` và
`notifications`. Làm `dealers` và `auth` trước thì ba module sau rẻ hơn nhiều.

### B-70 `dealers` (R2a)

Showroom, nhà phân phối, xưởng dịch vụ, trạm sạc. Mỗi điểm có toạ độ, khu vực
phụ trách, giờ mở cửa, và tập dịch vụ cung cấp tại điểm đó. Là dữ liệu nền nên
schema phải ổn định; đổi schema phải báo R2b.
*Chặn bởi:* Q3 trong [PRD web](web-prd.md) — dữ liệu đại lý lấy từ đâu.

### B-71 `inventory` (R2a)

Tồn kho theo VIN: xe cụ thể nào đang ở điểm nào, trạng thái ra sao. Phải trả lời
được "dòng xe này còn xe giao ngay ở tỉnh X không". Cần `dealers` trước.

### B-72 `auth` (R2b)

Đăng nhập khách hàng, nhân viên bán hàng, quản trị đại lý. Ba nhóm quyền khác
nhau trên cùng một hệ thống.
*Chặn bởi:* Q5 trong PRD web (có bắt đăng nhập mới đặt cọc không) và Q-B3 dưới
đây (phương thức xác thực).

### B-73 `users` (R2b)

Hồ sơ khách hàng và lead. Phải phân biệt được lead chưa xác thực với khách đã có
tài khoản, vì đặt cọc hiện không cần đăng nhập.
*Ràng buộc:* chứa PII — xem [SECURITY.md](../SECURITY.md).

### B-74 `testdrive` (R2b)

Đăng ký lái thử theo đại lý và khung giờ. Cần `dealers` trước. Phải chặn được
đăng ký trùng khung giờ tại cùng một điểm.

### B-75 `payments` (R2b)

Hai loại giao dịch khác hẳn nhau: thanh toán một lần (tiền cọc) và thuê bao định
kỳ (phí thuê pin hằng tháng). Ép chung một mô hình sẽ sai.
Phải mở được API chuyển trạng thái đơn (B-53) và giữ được B-50: thanh toán không
được làm đổi snapshot.
*Chặn bởi:* Q-B1 — cần một decision doc riêng trước khi viết dòng code nào. Đây
là ranh giới tiền bạc, theo plan P1 mục 7.

### B-76 `notifications` (R2b)

Thông báo trạng thái đơn và nhắc lịch lái thử, qua email và SMS. Phải chống gửi
trùng và ghi lại được đã gửi gì cho ai lúc nào.

## 11. Yêu cầu phi chức năng

**N-B1 — Test là điều kiện của mọi quy tắc nghiệp vụ.** Hiện có 60 test (53
`api`, 7 eval `ai`). Một quy tắc tiền bạc mới mà không có test âm tính là không
hoàn tất.

**N-B2 — Service là hàm thuần.** Nhận dữ liệu qua tham số, không tự truy vấn
CSDL, không biết HTTP. Đây là thứ làm cho quy tắc khó test trở nên dễ test.

**N-B3 — Contract sinh từ code, không viết tay.** CI chạy
`python scripts/generate-contract.py --check`.

**N-B4 — Test không phụ thuộc Docker.** Chạy trên SQLite. Test cần Docker là test
không ai chạy.

**N-B5 — Migration chạy được cả hai chiều.** Upgrade và downgrade. Hiện mới kiểm
chứng trên SQLite.

**N-B6 — Không bí mật trong repo.** gitleaks quét toàn bộ lịch sử trong CI.

## 12. Câu hỏi mở — chặn việc, cần quyết định

Nối tiếp Q1..Q6 của [PRD web](web-prd.md). Mặc định cấu hình được không phải là
authority; không tự chọn thay cho các câu hỏi này.

| # | Câu hỏi | Chặn | Ai quyết |
| --- | --- | --- | --- |
| Q-B1 | Cổng thanh toán nào, mô hình thuê bao ra sao, xử lý hoàn tiền thế nào? | B-75, và gián tiếp B-53 | Sản phẩm + R2b + pháp lý |
| Q-B2 | Khi nào thay biểu phí mẫu trong `api/seed.py` bằng biểu phí pháp lý đã đối chiếu? | **Điều kiện bắt buộc trước production** | Sản phẩm + R2a |
| Q-B3 | Phương thức xác thực: OTP qua số điện thoại, mật khẩu, hay nhà cung cấp bên thứ ba? | B-72, B-73 | Sản phẩm + R2b |
| Q-B4 | Nhà cung cấp LLM nào, trần chi phí bao nhiêu? | Adapter thật cho `ai/` (plan P1 mục 6) | R3 + R4a |
| Q-B5 | Đơn hàng và PII lưu bao lâu, xoá theo yêu cầu thế nào? | `users`, và tuân thủ pháp lý | Sản phẩm + pháp lý |
| Q-B6 | API có cần phiên bản không, và chính sách tương thích ngược ra sao? | Mọi thay đổi contract về sau | R2b + R1 |
| Q-B7 | Có cần mã lỗi máy đọc được thay cho `detail` tiếng Việt không? | Chất lượng xử lý lỗi ở `web/` | R2b + R1 |

## 13. Rủi ro đã biết

- **Biểu phí trong `api/seed.py` là dữ liệu mẫu chưa đối chiếu pháp lý.** Rủi ro:
  ai đó tưởng là số thật rồi đưa lên production. Đã cảnh báo trong chính file,
  trong `README.md` và trong `docs/RUNBOOK.md`. Phải thay trước khi lên production.
- **Chưa có xác thực.** `POST /orders` hiện ai gọi cũng được. Xem
  [SECURITY.md](../SECURITY.md).
- **B-55 chưa được thi hành chủ động.** Bất biến snapshot hiện được giữ bằng việc
  không có endpoint nào sửa đơn. Thêm một endpoint sửa đơn mà quên gọi
  `assert_snapshot_intact()` sẽ phá bất biến mà không test nào bắt được.
- **Mới kiểm chứng trên SQLite.** PostgreSQL có kiểu dữ liệu và ràng buộc chặt
  hơn; `Numeric`, `BigInteger` và `JSON` có thể hành xử khác. Là việc số 4 còn
  treo của plan P1.
