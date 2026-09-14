/**
 * Tiền hiển thị.
 *
 * Backend trả về số nguyên đồng. Frontend chỉ định dạng, **không tính toán**:
 * không cộng phí, không nhân phần trăm, không tự suy ra giá sau ưu đãi. Con số
 * sai trên trang bán xe là rủi ro pháp lý, và backend đã có nguồn sự thật.
 */
export function formatVnd(amount: number): string {
  return new Intl.NumberFormat("vi-VN").format(amount) + " VNĐ";
}
