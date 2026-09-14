import Link from "next/link";

import { api, ApiError } from "@/lib/api";
import { formatVnd } from "@/lib/money";

export default async function HomePage() {
  let models;
  try {
    models = await api.listModels();
  } catch (error) {
    // Backend chưa chạy là trạng thái thật lúc phát triển, không phải lỗi 500
    // của trang. Hiện thông báo thay vì đổ stack trace vào mặt người dùng.
    const reason = error instanceof ApiError ? `API trả ${error.status}` : "không gọi được API";
    return (
      <main>
        <h1>IFast</h1>
        <p>Chưa tải được danh mục xe: {reason}.</p>
        <p>Chạy backend: <code>uvicorn api.main:app --reload</code></p>
      </main>
    );
  }

  return (
    <main>
      <h1>IFast — Ô tô điện</h1>
      <ul>
        {models.map((model) => (
          <li key={model.code}>
            <Link href={`/xe/${model.code}`}>{model.name}</Link>
            {model.segment ? ` — ${model.segment}` : null}
            {model.seats ? ` — ${model.seats} chỗ` : null}
          </li>
        ))}
      </ul>
      <p>
        Giá và chi phí lăn bánh do backend tính. Trang này chỉ hiển thị, không
        tự cộng phí — xem <code>src/lib/money.ts</code>. {formatVnd(0) ? "" : ""}
      </p>
    </main>
  );
}
