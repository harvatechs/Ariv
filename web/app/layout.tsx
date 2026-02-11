import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ARIV Console",
  description: "Secure web control plane for ARIV"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
