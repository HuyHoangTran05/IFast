"use client";

import { ChevronDown, Menu, X } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

import styles from "./SiteHeader.module.css";

type HeaderVehicle = {
  code: string;
  name: string;
};

type SiteHeaderProps = {
  vehicles: HeaderVehicle[];
};

export function SiteHeader({ vehicles }: SiteHeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  function closeMenu() {
    setIsMenuOpen(false);
  }

  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link className={styles.brand} href="/" onClick={closeMenu}>
          IFast
        </Link>

        <button
          aria-controls="primary-navigation"
          aria-expanded={isMenuOpen}
          aria-label={isMenuOpen ? "Đóng menu điều hướng" : "Mở menu điều hướng"}
          className={styles.menuButton}
          onClick={() => setIsMenuOpen((isOpen) => !isOpen)}
          type="button"
        >
          {isMenuOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
        </button>

        <nav
          aria-label="Điều hướng chính"
          className={`${styles.navigation} ${isMenuOpen ? styles.navigationOpen : ""}`}
          id="primary-navigation"
        >
          <Link href="/xe" onClick={closeMenu}>
            Xe
          </Link>

          <details className={styles.vehicleMenu}>
            <summary>
              Danh sách xe <ChevronDown aria-hidden="true" size={16} />
            </summary>
            <div className={styles.vehicleMenuPanel}>
              {vehicles.length > 0 ? (
                vehicles.map((vehicle) => (
                  <Link href={`/xe/${vehicle.code}`} key={vehicle.code} onClick={closeMenu}>
                    {vehicle.name}
                  </Link>
                ))
              ) : (
                <span className={styles.unavailable}>Danh sách xe đang cập nhật</span>
              )}
            </div>
          </details>

          <span className={`${styles.secondaryLink} ${styles.unavailable}`}>Hỗ trợ đang cập nhật</span>
          <Link className={styles.primaryCta} href="/xe" onClick={closeMenu}>
            Đặt cọc
          </Link>
        </nav>
      </div>
    </header>
  );
}
