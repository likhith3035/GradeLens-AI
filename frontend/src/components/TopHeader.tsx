"use client";

import React, { useState } from "react";
import {
  Search,
  Sun,
  Moon,
  Bell,
  Cloud,
  ChevronDown,
  CheckCircle2,
  AlertTriangle,
  X,
  ExternalLink,
  Laptop
} from "lucide-react";
import { SystemHealth } from "../lib/types";

interface TopHeaderProps {
  health: SystemHealth | null;
  onModeSwitch: (mode: "local" | "online") => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  onSearchSubmit: (q: string) => void;
  pendingReviewCount: number;
  setActiveTab: (tab: string) => void;
}

export default function TopHeader({
  health,
  onModeSwitch,
  searchQuery,
  setSearchQuery,
  onSearchSubmit,
  pendingReviewCount,
  setActiveTab,
}: TopHeaderProps) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  const isLocal = health?.mode !== "online";

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      onSearchSubmit(searchQuery);
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between shrink-0 sticky top-0 z-30">
      {/* Search Bar with Ctrl K */}
      <div className="relative flex-1 max-w-md">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search students, roll numbers, colleges..."
            className="w-full bg-[#f8fafc] hover:bg-slate-50 focus:bg-white text-slate-800 placeholder-slate-400 text-xs pl-9 pr-14 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium"
          />
          <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 bg-white border border-slate-200 px-1.5 py-0.5 rounded font-semibold pointer-events-none shadow-2xs">
            Ctrl K
          </kbd>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3 ml-4">
        {/* Mode Toggle Group */}
        <div className="flex items-center gap-1.5 bg-slate-100/80 p-1 rounded-full border border-slate-200/60">
          <button
            onClick={() => onModeSwitch("local")}
            className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all ${
              isLocal
                ? "bg-emerald-100/90 text-emerald-800 shadow-2xs border border-emerald-300"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isLocal ? "bg-emerald-500 shadow-sm shadow-emerald-500/60 animate-pulse" : "bg-slate-400"
              }`}
            />
            Local Mode
          </button>

          <button
            onClick={() => onModeSwitch("online")}
            className={`px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all ${
              !isLocal
                ? "bg-blue-100 text-blue-800 shadow-2xs border border-blue-300"
                : "text-slate-500 hover:text-slate-800"
            }`}
          >
            <Cloud className="w-3.5 h-3.5" />
            Online Mode
          </button>
        </div>

        {/* Theme Toggle */}
        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          title="Toggle Theme"
          className="w-9 h-9 rounded-full flex items-center justify-center text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          {isDarkMode ? <Moon className="w-4 h-4 text-indigo-500" /> : <Sun className="w-4 h-4 text-amber-500" />}
        </button>

        {/* Notification Bell */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="w-9 h-9 rounded-full flex items-center justify-center text-slate-500 hover:text-slate-700 hover:bg-slate-100 transition-colors relative"
          >
            <Bell className="w-4 h-4" />
            {pendingReviewCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-4 h-4 bg-rose-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center border-2 border-white">
                {pendingReviewCount > 9 ? "9+" : pendingReviewCount}
              </span>
            )}
          </button>

          {/* Notifications Dropdown */}
          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-slate-200 p-4 z-50">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <span className="font-bold text-xs text-slate-800">Notifications & Alerts</span>
                <span className="text-[10px] bg-rose-50 text-rose-600 font-bold px-2 py-0.5 rounded-full">
                  {pendingReviewCount} Active
                </span>
              </div>
              <div className="py-2 space-y-2 max-h-60 overflow-y-auto">
                {pendingReviewCount > 0 ? (
                  <div
                    onClick={() => {
                      setActiveTab("review");
                      setShowNotifications(false);
                    }}
                    className="p-2.5 rounded-xl bg-amber-50/70 border border-amber-200 cursor-pointer hover:bg-amber-100/70 transition-all flex items-start gap-2.5"
                  >
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="text-xs font-semibold text-amber-900 leading-tight">
                        {pendingReviewCount} Memos Require Manual Review
                      </p>
                      <p className="text-[11px] text-amber-700 mt-0.5">
                        Calculation mismatches or unreadable roll numbers detected.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 text-center text-xs text-slate-400">
                    <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto mb-1" />
                    All records verified. No urgent alerts.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Profile Avatar */}
        <div className="relative">
          <button
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="flex items-center gap-2 pl-1.5 pr-2 py-1 rounded-full hover:bg-slate-100 transition-colors cursor-pointer"
          >
            <div className="w-8 h-8 rounded-full bg-[#0c1524] text-emerald-400 font-bold text-xs flex items-center justify-center shadow-xs border border-emerald-500/30">
              KL
            </div>
            <span className="text-xs font-bold text-slate-800">Kami Likhith</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {/* Profile Dropdown */}
          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-52 bg-white rounded-2xl shadow-xl border border-slate-200 py-2 z-50">
              <div className="px-4 py-2 border-b border-slate-100">
                <p className="text-xs font-bold text-slate-800">Kami Likhith</p>
                <p className="text-[11px] text-emerald-600 font-semibold">Lead Developer</p>
              </div>
              <a
                href="https://devlikhith.vercel.app/"
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between px-4 py-2 text-xs text-slate-600 hover:bg-slate-50 font-medium"
              >
                <span>Portfolio Website</span>
                <ExternalLink className="w-3 h-3 text-slate-400" />
              </a>
              <a
                href="https://github.com/likhith3035"
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-between px-4 py-2 text-xs text-slate-600 hover:bg-slate-50 font-medium"
              >
                <span>GitHub Profile</span>
                <ExternalLink className="w-3 h-3 text-slate-400" />
              </a>
              <div className="border-t border-slate-100 my-1" />
              <button
                onClick={() => {
                  setActiveTab("settings");
                  setShowProfileMenu(false);
                }}
                className="w-full text-left px-4 py-1.5 text-xs text-slate-600 hover:bg-slate-50 font-medium cursor-pointer"
              >
                System Settings
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
