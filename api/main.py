"""Điểm vào của API IFast.

File này là **append-only** theo luật trong `api/README.md`: R2a thêm router
mới bằng cách thêm dòng ở cuối khối include, không sắp xếp lại. Sắp xếp lại
danh sách này là nguồn conflict cố định giữa hai người backend.
"""

from __future__ import annotations

from fastapi import FastAPI

from api.battery.router import router as battery_router
from api.catalog.router import router as catalog_router
from api.orders.router import router as orders_router
from api.pricing.router import router as pricing_router
from api.promotions.router import router as promotions_router

app = FastAPI(
    title="IFast API",
    version="0.1.0",
    description="Nền tảng web bán ô tô điện.",
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# ── Đăng ký router — CHỈ THÊM DÒNG Ở CUỐI KHỐI NÀY ──────────────────────────
app.include_router(catalog_router)
app.include_router(pricing_router)
app.include_router(promotions_router)
app.include_router(battery_router)
app.include_router(orders_router)
