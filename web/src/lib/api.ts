/**
 * Cổng duy nhất ra backend.
 *
 * Kiểu dữ liệu sinh từ `contracts/openapi.yaml` bằng `npm run gen:api`, không
 * viết tay. Viết tay interface của backend là cách chắc chắn để frontend và
 * backend lệch nhau mà không ai biết cho tới khi khách nhìn thấy.
 *
 * `web/` không bao giờ gọi thẳng `ai/`. Tính năng AI đi qua endpoint của API.
 */

const BASE_URL = process.env.IFAST_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, params?: Record<string, string | number>): Promise<T> {
  const url = new URL(path, BASE_URL);
  for (const [key, value] of Object.entries(params ?? {})) {
    url.searchParams.set(key, String(value));
  }

  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) {
    const detail = await response.text();
    throw new ApiError(response.status, detail);
  }
  return (await response.json()) as T;
}

export type Spec = {
  motor_count: number | null;
  max_power_w: number | null;
  max_torque_nm: number | null;
  range_nedc_km: number | null;
  fast_charge_minutes: number | null;
  drivetrain: string | null;
};

export type Trim = { id: number; code: string; name: string; spec: Spec | null };

export type VehicleModel = {
  id: number;
  code: string;
  name: string;
  category: string;
  segment: string | null;
  seats: number | null;
  trims: Trim[];
  colors: { code: string; name: string; exterior: boolean }[];
};

export type OnRoadQuote = {
  as_of: string;
  province_code: string;
  ownership_model: string;
  vehicle_price_vnd: number;
  discount_vnd: number;
  monthly_battery_fee_vnd: number | null;
  items: { code: string; label: string; amount_vnd: number }[];
  promotions: { code: string; name: string; discount_vnd: number; terms_url: string | null }[];
  total_vnd: number;
};

export const api = {
  listModels: () => request<VehicleModel[]>("/catalog/models"),
  getModel: (code: string) => request<VehicleModel>(`/catalog/models/${code}`),
  onRoadQuote: (trimId: number, province: string) =>
    request<OnRoadQuote>("/pricing/on-road", { trim_id: trimId, province_code: province }),
};
