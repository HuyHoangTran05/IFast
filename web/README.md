# web — Web client

Owner: **R1 Frontend** (single owner).

Scope: toàn bộ giao diện web — trang public bán xe, khu vực tài khoản khách
hàng, portal đại lý. Routing, state, design system, component dùng chung.

Rules:

- Không gọi thẳng `ai/`. Mọi tính năng AI đi qua API của `api/`.
- Type của API được generate từ `contracts/openapi.yaml`, không viết tay.
- `web/src/components/ui/**` chỉ R1 được sửa, kể cả khi có người mượn route.
- E2E test thuộc `tests/e2e/` và do R4b viết. R1 viết unit/component test.
