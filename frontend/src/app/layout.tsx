import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "BoardBuy UAE — Billboard Marketplace",
  description: "Plan, book and measure outdoor advertising across the Emirates",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="sticky top-0 z-20 flex items-center gap-6 border-b border-white/10 bg-[#0e1014]/90 px-6 py-3 backdrop-blur">
          <Link href="/" className="text-lg font-extrabold">
            Board<span className="text-brand-gold">Buy</span> UAE
          </Link>
          <nav className="flex flex-1 gap-4 text-sm text-white/60">
            <Link href="/marketplace" className="hover:text-white">Marketplace</Link>
            <Link href="/campaigns" className="hover:text-white">My campaigns</Link>
          </nav>
          <Link
            href="/marketplace"
            className="rounded-lg bg-brand px-4 py-2 text-sm font-bold text-white"
          >
            Start a campaign
          </Link>
        </header>
        {children}
      </body>
    </html>
  );
}
