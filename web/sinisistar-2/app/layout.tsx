import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SiNiSistar 2 Walkthrough & Guide | Complete Item Database & Maps",
  description: "The ultimate English guide for SiNiSistar 2. Includes detailed boss strategies, interactive maps, relic locations, and a complete item database.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-50 min-h-screen">
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <a href="/" className="text-xl font-bold tracking-tighter text-red-500">
              SiNiSistar 2 <span className="text-slate-50">Guide</span>
            </a>
            <nav className="hidden md:flex gap-6 text-sm font-medium">
              <a href="/database" className="hover:text-red-400 transition-colors">Database</a>
              <a href="/maps" className="hover:text-red-400 transition-colors">Maps</a>
              <a href="/bosses" className="hover:text-red-400 transition-colors">Bosses</a>
              <a href="/relics" className="hover:text-red-400 transition-colors">Relics</a>
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="border-t border-slate-800 mt-20 py-10 bg-slate-900/30">
          <div className="container mx-auto px-4 text-center text-slate-500 text-sm">
            <p>&copy; 2026 SiNiSistar 2 Guide. All rights reserved.</p>
            <p className="mt-2">Created for the community by fans.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
