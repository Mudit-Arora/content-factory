import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "AI Content Creator",
  description: "Chat-first AI content creation platform"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
