import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@fontsource-variable/inter";
import "./globals.css";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { api } from "@/lib/api";

export const metadata: Metadata = {
  title: "IFast — Ô tô điện",
  description: "Nền tảng bán ô tô điện IFast.",
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  let vehicles: { code: string; name: string }[] = [];

  try {
    const models = await api.listModels();
    vehicles = models.map(({ code, name }) => ({ code, name }));
  } catch {
    // Header vẫn có thể render khi API chưa sẵn sàng ở môi trường phát triển.
  }

  return (
    <html lang="vi">
      <body>
        <div className="site-shell">
          <SiteHeader vehicles={vehicles} />
          {children}
          <SiteFooter />
        </div>
      </body>
    </html>
  );
}
