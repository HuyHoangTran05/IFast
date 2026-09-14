# contracts — Ranh giới giữa backend và client

Owner: **R2b**.

`openapi.yaml` là nguồn sự thật duy nhất cho API. R1 generate type từ đây và
code song song, không chờ backend làm xong.

File này **sinh từ backend**, không viết tay:

    python scripts/generate-contract.py           # ghi lại file
    python scripts/generate-contract.py --check   # CI dùng, fail nếu lệch

Viết tay OpenAPI cho hàng chục domain sẽ lệch khỏi code trong một tuần, và lúc
đó R1 code theo một tài liệu sai — tệ hơn là không có tài liệu. Đổi lại, CI
chạy `--check` nên mọi thay đổi contract đều lộ ra thành diff và không thể lọt
âm thầm vào một PR feature.

Phía web sinh type bằng `npm run gen:api`.

Luật:

- Đổi contract = PR **riêng**, dán nhãn `contract`, cần R1 approve.
- Không bao giờ sửa contract lẫn trong PR feature.
- `contracts/generated/**` là output của script — conflict thì chạy lại
  generator, không merge tay.
