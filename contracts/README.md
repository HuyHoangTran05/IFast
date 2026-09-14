# contracts — Ranh giới giữa backend và client

Owner: **R2b**.

`openapi.yaml` là nguồn sự thật duy nhất cho API. R1 generate type từ đây và
code song song, không chờ backend làm xong.

Luật:

- Đổi contract = PR **riêng**, dán nhãn `contract`, cần R1 approve.
- Không bao giờ sửa contract lẫn trong PR feature.
- `contracts/generated/**` là output của script — conflict thì chạy lại
  generator, không merge tay.
