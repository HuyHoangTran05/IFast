# Product Docs

This directory contains current consumer-product behavior derived from real
accepted intent. Harness deliberately ships no fake product domains.

When a user provides a product specification, derive smaller living documents
here instead of keeping one growing specification as the operating manual. Name
files after actual product domains, such as `overview.md`, `billing.md`,
`permissions.md`, or `api-conventions.md`.

## Current Product Contract

IFast documents live here:

- [backend-prd.md](backend-prd.md) — hành vi backend, B-01..B-76.
- [web-prd.md](web-prd.md) — hành vi web, F-01..F-21 và N-01..N-09.
- [api-conventions.md](api-conventions.md) — ngữ nghĩa tham số và mô hình lỗi.
- [data-model.md](data-model.md) — 13 bảng và luật migration.
- [web-sitemap.md](web-sitemap.md) — tuyến đường và nguồn dữ liệu từng trang.
- [web-design-system.md](web-design-system.md) — token và component.
- [glossary.md](glossary.md) — đối chiếu thuật ngữ.

Kiến trúc ở [../ARCHITECTURE.md](../ARCHITECTURE.md), bảo mật ở
[../SECURITY.md](../SECURITY.md).

## Update Rule

When behavior changes:

1. Update the affected product document when the expected behavior changed.
2. Update the active execution plan when complex work uses one.
3. Add a lasting decision only when future work must inherit a consequential
   product, architecture, data, security, compatibility, or validation choice.
4. Add or update executable proof that exercises the behavior.

Bounded changes do not require a parallel lifecycle record.
