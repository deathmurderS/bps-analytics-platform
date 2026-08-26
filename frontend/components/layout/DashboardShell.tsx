"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Sidebar from "./Sidebar";
import TopNavbar from "./TopNavbar";

interface DashboardShellProps {
  children: React.ReactNode;
}

export default function DashboardShell({ children }: DashboardShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex min-h-screen flex-col lg:pl-sidebar-width">
        <TopNavbar onMenuClick={() => setSidebarOpen(true)} />

        <main className="mx-auto w-full max-w-container flex-1 px-4 py-6 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
          >
            {children}
          </motion.div>
        </main>

        <footer className="border-t border-line bg-white px-4 py-4 sm:px-6">
          <div className="mx-auto flex w-full max-w-container flex-col items-center justify-between gap-2 text-center sm:flex-row sm:text-left">
            <p className="text-[11px] text-ink-muted">
              BPS Analytics Platform — Data dari BPS WebAPI melalui ETL pipeline
            </p>
            <p className="text-[11px] text-ink-muted">
              Sumber: Badan Pusat Statistik
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}