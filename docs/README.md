# Documentation Map

Start with the smallest authoritative surface.

## Current Product

- `WORKFLOW.md`: request shape, planning, judgment, operation, validation, and
  completion.
- `ARCHITECTURE.md`: current product, code, state, update, and ownership
  boundaries.
- [`repository-harness/docs/HARNESS.md`](../repository-harness/docs/HARNESS.md):
  product principles and installed-core model. Vendored upstream source; not
  part of the installed core listed in `.harness-core/manifest.json`.
- `product/`: current product behavior and installation contract.
- `decisions/`: lasting choices future work must inherit.
- `plans/`: one durable working-memory document for work that needs it.
- [`patterns/encoding-invariants.md`](patterns/encoding-invariants.md): turn
  accepted architecture, reliability, security, and quality rules into native
  mechanical validation.
- `templates/`: optional decision, plan, runbook, and Harness-improvement
  structures.

## Consumer-Owned Truth

The consumer's README, product documents, architecture, code, tests, CI,
runtime signals, and application behavior remain authoritative. Harness does
not overwrite those with upstream product assumptions.

## Source Repository

- Root `README.md`: product overview, installation, maintenance, EOL, and
  development.
- `crates/harness/`: safe core installer/updater.
- `scripts/`: platform bootstrap, release, and validation entrypoints.
- `tests/`: behavior ownership and repository contract.

## History

The former SQLite control plane, protocol v1, story packets, migration evidence,
and compatibility documentation are preserved by Git history and immutable
`harness-cli-v*` tags. They are intentionally absent from the current tree so
search and agent retrieval return current product authority.

## Tài liệu của IFast

- [HANDOFF.md](HANDOFF.md) — bàn giao: chạy gì trước, việc tiếp theo, bẫy đã biết.
- [RUNBOOK.md](RUNBOOK.md) — chạy, reset trạng thái, gỡ lỗi, dọn dẹp.
- [plans/active/p1-nen-tang-ban-xe.md](plans/active/p1-nen-tang-ban-xe.md) — tiến độ và quyết định.
- [decisions/](decisions/) — phân vai và ranh giới sở hữu.
- [product/web-prd.md](product/web-prd.md) — PRD trải nghiệm web bán xe: yêu cầu chức năng, phi chức năng, câu hỏi mở.
- [product/web-sitemap.md](product/web-sitemap.md) — danh mục tuyến đường của `web/` và nguồn dữ liệu từng trang.
- [product/web-design-system.md](product/web-design-system.md) — token, component, và luật hiển thị tiền.
- [plans/active/p2-trai-nghiem-ban-xe-tren-web.md](plans/active/p2-trai-nghiem-ban-xe-tren-web.md) — giai đoạn web, thứ tự thực thi.
- [prompts/](prompts/) — prompt soạn sẵn cho các đợt làm việc lặp lại.
- [ARCHITECTURE.md](ARCHITECTURE.md) — thành phần, đường may, bốn bất biến, và những gì chưa có.
- [SECURITY.md](SECURITY.md) — tài sản, hiện trạng thật, và 12 điều kiện trước production.
- [product/backend-prd.md](product/backend-prd.md) — PRD backend: B-01..B-76, trạng thái từng domain, câu hỏi mở.
- [product/api-conventions.md](product/api-conventions.md) — ngữ nghĩa `as_of`, mô hình lỗi, quy ước đặt tên.
- [product/data-model.md](product/data-model.md) — 13 bảng, ba nhóm, luật migration.
- [product/glossary.md](product/glossary.md) — đối chiếu thuật ngữ Việt–Anh–tên trong code.
