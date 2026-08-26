"use client";

import { useState } from "react";
import { Bell, Menu, Search, RefreshCw } from "lucide-react";

interface TopNavbarProps {
  onMenuClick: () => void;
}

export default function TopNavbar({ onMenuClick }: TopNavbarProps) {
  const [lastUpdated] = useState("20 Agu 2026, 10:00 WIB");

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-line bg-white px-4 sm:px-6">
      {/* Mobile menu toggle */}
      <button
        onClick={onMenuClick}
        className="text-ink-soft hover:text-ink lg:hidden"
        aria-label="Buka menu"
      >
        <Menu className="h-6 w-6" />
      </button>

      {/* Search */}
      <div className="relative hidden flex-1 max-w-md sm:block">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint" />
        <input
          type="search"
          placeholder="Cari indikator, provinsi, komoditas..."
          className="input w-full pl-9"
        />
      </div>

      <div className="flex-1 sm:hidden" />

      {/* Right actions */}
      <div className="flex items-center gap-1.5 sm:gap-3">
        <button
          className="btn-ghost hidden items-center gap-1.5 text-xs text-ink-muted sm:inline-flex"
          title="Perbarui data"
        >
          <RefreshCw className="h-4 w-4" />
          Perbarui
        </button>

        <div className="hidden text-right sm:block">
          <p className="text-[11px] font-medium leading-4 text-ink-soft">
            Data terakhir diperbarui
          </p>
          <p className="text-[11px] leading-4 text-ink-muted">{lastUpdated}</p>
        </div>

        <button
          className="relative rounded p-2 text-ink-soft transition-colors hover:bg-slate-100 hover:text-ink"
          aria-label="Notifikasi"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-primary" />
        </button>
      </div>
    </header>
  );
}