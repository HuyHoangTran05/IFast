import Link from "next/link";

import styles from "./SiteFooter.module.css";

export function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <div className={styles.brandBlock}>
          <Link className={styles.brand} href="/">
            IFast
          </Link>
          <p>Nền tảng trải nghiệm và đặt cọc ô tô điện.</p>
        </div>

        <nav aria-label="Điều hướng chân trang" className={styles.links}>
          <div>
            <h2>Khám phá</h2>
            <Link href="/xe">Danh sách xe</Link>
            <Link href="/xe">Đặt cọc</Link>
          </div>
          <div>
            <h2>Hỗ trợ</h2>
            <span>Showroom đang cập nhật</span>
            <span>Chính sách đang cập nhật</span>
          </div>
        </nav>
      </div>
      <div className={styles.legal}>
        <p>© 2026 IFast. Nội dung minh hoạ cho giai đoạn P2.</p>
      </div>
    </footer>
  );
}
