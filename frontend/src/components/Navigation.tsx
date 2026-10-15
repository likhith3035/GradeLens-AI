"use client";

import React from "react";
import {
  GraduationCap,
  LayoutDashboard,
  Upload,
  ListOrdered,
  CheckCircle2,
  User,
  BarChart3,
  PieChart,
  FileSpreadsheet,
  Clock,
  Settings,
  ChevronRight,
  HardDrive
} from "lucide-react";
import { SystemHealth } from "../lib/types";

interface NavigationProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  health: SystemHealth | null;
  pendingReviewCount: number;
  totalMemos?: number;
  recentDocsCount?: number;
}

export default function Navigation({
  activeTab,
  setActiveTab,
  health,
  pendingReviewCount,
  totalMemos = 0,
  recentDocsCount = 0,
}: NavigationProps) {
  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "upload", label: "Upload Memos", icon: Upload },
    {
      id: "queue",
      label: "Processing Queue",
      icon: ListOrdered,
      badge: recentDocsCount > 0 ? recentDocsCount : undefined,
      badgeColor: "bg-rose-500 text-white",
    },
    {
      id: "review",
      label: "Verification",
      icon: CheckCircle2,
      badge: pendingReviewCount > 0 ? pendingReviewCount : undefined,
      badgeColor: "bg-rose-500 text-white",
    },
    { id: "students", label: "Students", icon: User },
    { id: "analytics", label: "Academic Analytics", icon: BarChart3 },
    { id: "backlogs", label: "Backlog Analysis", icon: PieChart },
    { id: "export", label: "Excel Exports", icon: FileSpreadsheet },
    { id: "history", label: "History", icon: Clock },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const storageLabel = totalMemos > 0 ? `${(totalMemos * 1.8).toFixed(1)} MB / 10 GB` : "0.0 MB / 10 GB";
  const storageWidth = totalMemos > 0 ? `${Math.min(100, Math.max(2, totalMemos * 1.5))}%` : "0%";

  return (
    <aside className="w-64 bg-[#0c1524] text-slate-300 flex flex-col shrink-0 border-r border-slate-800/80 select-none h-screen sticky top-0 justify-between">
      {/* Brand Header */}
      <div>
        <div className="p-5 flex items-center gap-3 border-b border-slate-800/60">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-sky-500 to-blue-600 flex items-center justify-center text-white shadow-lg shadow-cyan-500/20 shrink-0">
            <GraduationCap className="w-5 h-5 text-cyan-100" />
          </div>
          <div>
            <h1 className="font-bold text-white text-base tracking-tight leading-tight">MemoScan AI</h1>
            <p className="text-[11px] text-slate-400 font-medium">Marks & Analytics</p>
          </div>
        </div>

        {/* Menu Items */}
        <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-230px)]">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id || (activeTab === "overview" && item.id === "dashboard");

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id === "dashboard" ? "overview" : item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                  isActive
                    ? "bg-[#064e3b] text-white shadow-sm border border-emerald-500/30"
                    : "text-slate-300 hover:bg-slate-800/50 hover:text-white"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon
                    className={`w-4 h-4 ${
                      isActive ? "text-emerald-400" : "text-slate-400 group-hover:text-slate-200"
                    }`}
                  />
                  <span>{item.label}</span>
                </div>

                {item.badge !== undefined && item.badge > 0 && (
                  <span
                    className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold min-w-4 text-center ${
                      item.badgeColor || "bg-rose-500 text-white"
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Footer Section */}
      <div className="p-4 border-t border-slate-800/60 space-y-3 bg-[#0a111e]">
        {/* Local Mode Card */}
        <div
          onClick={() => setActiveTab("settings")}
          className="p-3 rounded-2xl bg-[#131d2e] border border-slate-700/60 hover:border-slate-600 transition-all flex items-center justify-between cursor-pointer group"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-emerald-950 border border-emerald-600/50 flex items-center justify-center relative">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping absolute opacity-75" />
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            </div>
            <div>
              <p className="text-xs font-bold text-white leading-tight">Local Mode</p>
              <p className="text-[10px] text-slate-400">Running on this device</p>
            </div>
          </div>
          <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300 group-hover:translate-x-0.5 transition-all" />
        </div>

        {/* Storage Usage Bar */}
        <div className="px-1 space-y-1.5">
          <div className="flex items-center justify-between text-[11px]">
            <span className="text-slate-400 font-medium">Storage Usage</span>
            <span className="text-slate-200 font-bold">{storageLabel}</span>
          </div>
          <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-500"
              style={{ width: storageWidth }}
            />
          </div>
        </div>

        {/* Developer Attribution */}
        <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-[10px] text-slate-400 px-1">
          <span>By <a href="https://devlikhith.vercel.app/" target="_blank" rel="noreferrer" className="text-emerald-400 hover:underline font-bold">Kami Likhith</a></span>
          <a href="https://github.com/likhith3035" target="_blank" rel="noreferrer" className="hover:text-slate-200 transition-colors">GitHub ↗</a>
        </div>
      </div>
    </aside>

  );
}
