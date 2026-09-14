import { notFound } from "next/navigation";

import { api, ApiError } from "@/lib/api";
import { formatVnd } from "@/lib/money";

type Props = { params: Promise<{ code: string }> };

export default async function VehiclePage({ params }: Props) {
  const { code } = await params;

  let model;
  try {
    model = await api.getModel(code);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) notFound();
    throw error;
  }

  const trim = model.trims[0];
  const spec = trim?.spec;

  return (
    <main>
      <h1>{model.name}</h1>

      <h2>Thông số kỹ thuật</h2>
      {spec ? (
        <dl>
          <dt>Quãng đường (NEDC)</dt>
          <dd>{spec.range_nedc_km} km</dd>
          <dt>Công suất tối đa</dt>
          <dd>{spec.max_power_w} W</dd>
          <dt>Mô men xoắn cực đại</dt>
          <dd>{spec.max_torque_nm} Nm</dd>
          <dt>Sạc nhanh</dt>
          <dd>{spec.fast_charge_minutes} phút</dd>
          <dt>Dẫn động</dt>
          <dd>{spec.drivetrain}</dd>
        </dl>
      ) : (
        <p>Chưa có thông số.</p>
      )}

      <h2>Màu sắc</h2>
      <ul>
        {model.colors.map((color) => (
          <li key={color.code}>{color.name}</li>
        ))}
      </ul>

      {trim ? <OnRoad trimId={trim.id} /> : null}
    </main>
  );
}

async function OnRoad({ trimId }: { trimId: number }) {
  let quote;
  try {
    quote = await api.onRoadQuote(trimId, "HN");
  } catch {
    // Tỉnh chưa có biểu phí thì backend trả 404. Không được đoán, không được
    // hiển thị giá xe như thể đó là giá lăn bánh.
    return <p>Chưa có dự toán lăn bánh cho khu vực này.</p>;
  }

  return (
    <>
      <h2>Dự toán chi phí lăn bánh — Hà Nội</h2>
      <table>
        <tbody>
          {quote.items.map((item) => (
            <tr key={item.code}>
              <td>{item.label}</td>
              <td>{formatVnd(item.amount_vnd)}</td>
            </tr>
          ))}
          <tr>
            <td>
              <strong>Tổng</strong>
            </td>
            <td>
              <strong>{formatVnd(quote.total_vnd)}</strong>
            </td>
          </tr>
        </tbody>
      </table>
      {quote.promotions.length > 0 ? (
        <p>
          Ưu đãi đang áp dụng: {quote.promotions.map((p) => p.name).join(", ")}. Áp dụng theo điều
          khoản và điều kiện.
        </p>
      ) : null}
      {quote.monthly_battery_fee_vnd ? (
        <p>Phí thuê pin hằng tháng: {formatVnd(quote.monthly_battery_fee_vnd)}</p>
      ) : null}
    </>
  );
}
