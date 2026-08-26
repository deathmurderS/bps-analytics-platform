"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  LineChart,
  Map,
  ArrowLeftRight,
  BookOpenText,
  X,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/economic", label: "Ekonomi", icon: LineChart },
  { href: "/regional", label: "Regional", icon: Map },
  { href: "/trade", label: "Perdagangan", icon: ArrowLeftRight },
  { href: "/metadata", label: "Metadata", icon: BookOpenText },
];

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-sidebar-width flex-col bg-sidebar-bg transition-transform duration-200 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Brand */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-6">
          <Link href="/" className="flex items-center gap-2.5" onClick={onClose}>
            <span className="flex h-8 w-8 items-center justify-center rounded bg-primary text-sm font-bold text-white">
              BPS
            </span>
            <span className="text-[15px] font-semibold tracking-tight text-white">
              Analytics
            </span>
          </Link>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white lg:hidden"
            aria-label="Tutup menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          <p className="px-6 pb-2 label-caps text-slate-500">Menu Utama</p>
          <ul className="space-y-0.5">
            {NAV_ITEMS.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);
              const Icon = item.icon;
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    onClick={onClose}
                    className={`relative flex items-center gap-3 px-6 py-2.5 text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-sidebar-hover text-white"
                        : "text-sidebar-text hover:bg-sidebar-hover hover:text-white"
                    }`}
                  >
                    {isActive && (
                      <motion.span
                        layoutId="sidebar-active"
                        className="absolute left-0 top-0 h-full w-[3px] rounded-r bg-primary"
                        transition={{ type: "spring", stiffness: 400, damping: 32 }}
                      />
                    )}
                    <Icon className="h-[18px] w-[18px]" strokeWidth={1.75} />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="border-t border-slate-800 px-6 py-4">
          <p className="text-[11px] leading-4 text-slate-500">
            BPS Analytics Platform
            <br />
            Data • Insight • Keputusan
          </p>
        </div>
      </aside>
    </>
  );
}