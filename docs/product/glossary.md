# Từ điển thuật ngữ

Đội sáu người viết tài liệu tiếng Việt và viết code tiếng Anh. Bảng này chốt
cách dịch, để một khái niệm không mang hai cái tên trong hai file.

Cột **Trong code** là tên thật đang dùng — tra được bằng `grep`.

## 1. Sản phẩm

| Tiếng Việt | Tiếng Anh | Trong code | Nghĩa |
| --- | --- | --- | --- |
| Dòng xe | model | `VehicleModel`, `catalog_vehicle_model` | Một dòng sản phẩm, ví dụ VF 2. Có mã `code` duy nhất |
| Phiên bản | trim | `Trim`, `catalog_trim` | Biến thể của một dòng xe. **Giá gắn ở đây**, không gắn ở dòng xe |
| Thông số | spec | `Spec`, `catalog_spec` | Mỗi đại lượng một cột có kiểu, không phải văn bản tự do |
| Loại sản phẩm | product category | `ProductCategory` | `car` hoặc `motorbike`; hai loại đo bằng đơn vị khác nhau |
| Màu ngoại thất | exterior colour | `Color.exterior = True` | Phân biệt với màu nội thất |
| Tầm hoạt động NEDC | NEDC range | `range_nedc_km` | Dùng cho ô tô |
| Quãng đường mỗi lần sạc | range per charge | `range_per_charge_km` | Dùng cho xe máy điện |

## 2. Giá và chi phí

| Tiếng Việt | Tiếng Anh | Trong code | Nghĩa |
| --- | --- | --- | --- |
| Mô hình sở hữu | ownership model | `OwnershipModel` | `battery_included` (kèm pin) hoặc `battery_lease` (thuê pin). **Hai biến thể giá, không phải một cờ** |
| Giá niêm yết | list price | `list_price_vnd` | Giá công bố của một phiên bản theo một mô hình sở hữu |
| Phí thuê pin hằng tháng | monthly battery fee | `monthly_battery_fee_vnd` | Chỉ có nghĩa với mô hình thuê pin |
| Chi phí lăn bánh | on-road cost | `OnRoadQuote`, `/pricing/on-road` | Tổng tiền khách phải trả để xe lăn bánh hợp pháp tại một tỉnh |
| Lệ phí trước bạ | registration tax | `registration_tax_rate`, khoản `registration_tax` | Tính **trên giá sau khi trừ ưu đãi**, tỉ lệ khác nhau theo tỉnh |
| Phí đăng ký biển số | plate fee | `plate_fee_vnd` | |
| Phí đăng kiểm | inspection fee | `inspection_fee_vnd` | |
| Phí đường bộ | road fee | `road_fee_year_vnd` | Tính cho một năm |
| Bảo hiểm TNDS bắt buộc | compulsory civil liability insurance | `civil_insurance_year_vnd` | Bắt buộc theo luật |
| Phí dịch vụ đăng ký | service fee | `service_fee_vnd` | |
| Khoản chi phí | line item | `LineItem` | Một dòng trong phần tách khoản |
| Phần tách khoản | breakdown | `OnRoadQuote.items` | Bảy khoản đi cùng tổng, không tách rời |
| Chi phí vận hành | running cost | `RunningCostComparison` | So sánh tiền nhiên liệu hằng tháng giữa xe điện và xe xăng dầu |
| Biểu phí | fee schedule | `RegistrationFeeSchedule` | Bảng phí khoá theo tỉnh, có khoảng hiệu lực |

## 3. Ưu đãi

| Tiếng Việt | Tiếng Anh | Trong code | Nghĩa |
| --- | --- | --- | --- |
| Ưu đãi | promotion | `Promotion` | Thực thể có vòng đời, không phải một cột giảm giá |
| Ưu đãi tiền mặt | fixed amount | `FIXED_AMOUNT` | Giảm một số tiền cố định |
| Ưu đãi phần trăm | percent of price | `PERCENT_OF_PRICE` | Giảm theo tỉ lệ giá xe |
| Ưu đãi hiện vật | benefit in kind | `BENEFIT_IN_KIND` | Ví dụ miễn phí sạc. Giảm 0 đồng nhưng **vẫn được liệt kê** |
| Cộng dồn được | stackable | `Promotion.stackable` | Áp cùng lúc với ưu đãi cộng dồn khác |
| Không cộng dồn | exclusive | `stackable = False` | Đứng một mình |
| Độ ưu tiên | priority | `Promotion.priority` | Tiêu chí đầu tiên khi chọn ưu đãi không cộng dồn tốt nhất |

## 4. Thời gian — nhóm quan trọng nhất

| Tiếng Việt | Tiếng Anh | Trong code | Nghĩa |
| --- | --- | --- | --- |
| Mốc thời gian tính | as of | `as_of` | "Tính như thể hôm đó". Bỏ trống là hôm nay **theo giờ Việt Nam** |
| Ngày nghiệp vụ | business date | `api/core/clock.py::today()` | Ngày ở Việt Nam, không phải ngày ở máy chủ |
| Khoảng hiệu lực | effective period | `effective_from`, `effective_to` | Nửa mở: `from <= as_of < to`. `to = null` nghĩa là còn hiệu lực |
| Bảng chính sách | policy table | Mọi bảng có `effective_from` | Không có "bản ghi hiện tại", chỉ có bản ghi hiệu lực tại một mốc |
| Ngày báo giá | quoted on | `Order.quoted_on` | Mốc đã dùng để tính mọi con số trong snapshot |
| Thời điểm hình thành tài sản | formed on | `BatteryAsset.formed_on` | Mốc tra **chính sách bảo hành** pin |
| Thời điểm xảy ra sự cố | incident on | `incident_on` | Mốc tra **giá pin công bố** |

Hai dòng cuối là hai mốc khác nhau trong cùng một công thức. Nhầm chúng với nhau
là tính sai tiền của khách.

## 5. Pin thuê

| Tiếng Việt | Tiếng Anh | Trong code | Nghĩa |
| --- | --- | --- | --- |
| Tài sản pin | battery asset | `BatteryAsset` | Pin có định danh `serial`, vòng đời tách khỏi chiếc xe |
| Giá pin công bố | list price (A) | `BatteryListPrice`, `A` | Tra tại thời điểm xảy ra sự cố |
| Thời gian sử dụng | months of use (T1) | `months_of_use()`, `T1` | Tính tròn theo tháng, luật 15 ngày |
| Thời gian bảo hành | warranty months (T2) | `warranty_months`, `T2` | Theo chính sách tại thời điểm hình thành tài sản |
| Luật làm tròn 15 ngày | 15-day rounding | `ROUND_UP_FROM_DAYS` | Dư từ 15 ngày tính thêm một tháng, dưới 15 ngày bỏ |
| Sàn bồi thường | compensation floor | `MINIMUM_COMPENSATION_RATE` | 10% của giá công bố; thiếu nó thì ra số âm |
| Bồi thường | compensation (B) | `compute_compensation()` | `B = A × (1 − T1/T2)`, không thấp hơn sàn |

## 6. Đơn hàng

| Tiếng Việt | Tiếng Anh | Trong code | Nghĩa |
| --- | --- | --- | --- |
| Đặt cọc | deposit | `OrderChannel.DEPOSIT` | Luồng mua ô tô: cọc → hợp đồng → giao xe |
| Mua thẳng | direct purchase | `DIRECT_PURCHASE` | Luồng mua xe máy và phụ kiện |
| Snapshot | snapshot | `price_snapshot` | Ảnh chụp bất biến. **Không dịch** — dùng nguyên chữ trong cả hai ngôn ngữ |
| Tiền cọc | deposit amount | `deposit_vnd` | Không âm, không vượt tổng giá trị đơn |
| Mã đơn | order code | `Order.code` | Tra cứu được, không cần đăng nhập |

## 7. Kỹ thuật

| Tiếng Việt | Tiếng Anh | Trong code | Nghĩa |
| --- | --- | --- | --- |
| Đường may | seam | — | Chỗ hai người phải đồng ý; mỗi đường may có một cơ chế máy móc giữ |
| Bất biến | invariant | — | Điều luôn đúng, có file chịu trách nhiệm thi hành |
| Contract | contract | `contracts/openapi.yaml` | Sinh từ code, không viết tay. **Không dịch** |
| Hàm thuần | pure function | Mọi hàm trong `*/service.py` | Nhận dữ liệu qua tham số, không truy vấn CSDL, không biết HTTP |
| Số nguyên đồng | integer VND | `Vnd = int` | Không `float` cho tiền, ở bất kỳ đâu |
| Quy ước nhân 10 | times-ten convention | hậu tố `_x10` | 6,5 truyền vào là `65` |
| Dữ liệu mẫu | sample data | `api/seed.py` | **Chưa đối chiếu pháp lý**, phải thay trước production |

## 8. Cách dùng bảng này

- Thêm thuật ngữ mới vào đây **cùng PR** với code giới thiệu nó.
- Tên trong code là nguồn sự thật. Bảng này lệch với code thì sửa bảng, không sửa
  code cho khớp bảng.
- Ba chữ giữ nguyên tiếng Anh vì dịch ra làm mất nghĩa: **snapshot**,
  **contract**, **trim**.
