"use client";

import { CircleAlert, Inbox, LoaderCircle } from "lucide-react";

import styles from "./DataStates.module.css";

type StateProps = {
  title: string;
  message?: string;
};

export function LoadingState({ title, message = "Đang tải dữ liệu, vui lòng chờ." }: StateProps) {
  return (
    <section aria-busy="true" aria-live="polite" className={styles.state}>
      <LoaderCircle aria-hidden="true" className={styles.spinner} size={32} />
      <div>
        <h2>{title}</h2>
        <p>{message}</p>
      </div>
    </section>
  );
}

export function EmptyState({ title, message = "Hiện chưa có dữ liệu để hiển thị." }: StateProps) {
  return (
    <section className={styles.state}>
      <Inbox aria-hidden="true" size={32} />
      <div>
        <h2>{title}</h2>
        <p>{message}</p>
      </div>
    </section>
  );
}

type ErrorStateProps = StateProps & {
  onRetry?: () => void;
  retryLabel?: string;
};

export function ErrorState({
  title,
  message = "Không thể tải dữ liệu. Vui lòng thử lại.",
  onRetry,
  retryLabel = "Thử lại",
}: ErrorStateProps) {
  return (
    <section aria-live="assertive" className={`${styles.state} ${styles.error}`} role="alert">
      <CircleAlert aria-hidden="true" size={32} />
      <div>
        <h2>{title}</h2>
        <p>{message}</p>
        <button onClick={onRetry ?? (() => window.location.reload())} type="button">
          {retryLabel}
        </button>
      </div>
    </section>
  );
}
