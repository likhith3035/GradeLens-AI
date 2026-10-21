"use client";

import React, { useState, useEffect } from "react";
import Navigation from "../components/Navigation";
import TopHeader from "../components/TopHeader";
import OverviewTab from "../components/OverviewTab";
import UploadTab from "../components/UploadTab";
import ProcessingQueueTab from "../components/ProcessingQueueTab";
import ReviewTab from "../components/ReviewTab";
import StudentsTab from "../components/StudentsTab";
import AnalyticsTab from "../components/AnalyticsTab";
import BacklogsTab from "../components/BacklogsTab";
import ExportTab from "../components/ExportTab";
import HistoryTab from "../components/HistoryTab";
import SettingsTab from "../components/SettingsTab";
import { fetchHealth, fetchAnalytics, fetchReviewQueue, updateMode, fetchRecentDocuments } from "../lib/api";
import { SystemHealth, AnalyticsFull } from "../lib/types";
import { Menu } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("overview");
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsFull | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [pendingReviewCount, setPendingReviewCount] = useState(0);
  const [recentDocsCount, setRecentDocsCount] = useState(0);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  const refreshData = async () => {
    try {
      const h = await fetchHealth();
      setHealth(h);
    } catch (e) {
      console.warn("Backend not yet connected on port 8000:", e);
    }

    try {
      setAnalyticsLoading(true);
      const a = await fetchAnalytics();
      setAnalytics(a);
      setPendingReviewCount(a.overview.records_requiring_verification);
    } catch (e) {
      console.warn("Analytics load error:", e);
    } finally {
      setAnalyticsLoading(false);
    }

    try {
      const q = await fetchReviewQueue();
      setPendingReviewCount(q.length);
    } catch {
      setPendingReviewCount(0);
    }

    try {
      const recent = await fetchRecentDocuments(10);
      setRecentDocsCount(recent.length);
    } catch {
      setRecentDocsCount(0);
    }
  };

  useEffect(() => {
    let ignore = false;
    void Promise.allSettled([
      fetchHealth(),
      fetchAnalytics(),
      fetchReviewQueue(),
      fetchRecentDocuments(10)
    ]).then(([hRes, aRes, qRes, rRes]) => {
      if (ignore) return;
      if (hRes.status === "fulfilled") setHealth(hRes.value);
      if (aRes.status === "fulfilled") {
        setAnalytics(aRes.value);
        setPendingReviewCount(aRes.value.overview.records_requiring_verification);
      }
      if (qRes.status === "fulfilled") setPendingReviewCount(qRes.value.length);
      if (rRes.status === "fulfilled") setRecentDocsCount(rRes.value.length);
      setAnalyticsLoading(false);
    });

    return () => {
      ignore = true;
    };
  }, []);

  const handleModeSwitch = async (mode: "local" | "online") => {
    try {
      await updateMode(mode);
      await refreshData();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Mode switch failed";
      alert(`Mode switch failed: ${msg}`);
    }
  };

  const handleSearchSubmit = (q: string) => {
    if (q.trim()) {
      setActiveTab("students");
    }
  };

  const totalMemos = analytics?.overview.total_memos_processed ?? 0;

  return (
    <div className="flex h-screen bg-[#f4f7fb] overflow-hidden font-sans">
      {/* Sidebar for Desktop */}
      <div className="hidden md:flex shrink-0">
        <Navigation
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          health={health}
          pendingReviewCount={pendingReviewCount}
          totalMemos={totalMemos}
          recentDocsCount={recentDocsCount}
        />
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div className="fixed inset-0 bg-slate-900/60" onClick={() => setMobileMenuOpen(false)} />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-[#0c1524]">
            <Navigation
              activeTab={activeTab}
              setActiveTab={(tab) => {
                setActiveTab(tab);
                setMobileMenuOpen(false);
              }}
              health={health}
              pendingReviewCount={pendingReviewCount}
              totalMemos={totalMemos}
              recentDocsCount={recentDocsCount}
            />
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile Header (Hidden on Desktop) */}
        <header className="md:hidden bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-lg text-slate-600 hover:bg-slate-100"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div className="font-bold text-sm text-slate-800">MemoScan AI</div>
          <div className="w-8" />
        </header>

        {/* Desktop Top Header Bar */}
        <div className="hidden md:block">
          <TopHeader
            health={health}
            onModeSwitch={handleModeSwitch}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            onSearchSubmit={handleSearchSubmit}
            pendingReviewCount={pendingReviewCount}
            setActiveTab={setActiveTab}
          />
        </div>

        {/* Scrollable Page Canvas */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-7">
          <div className="max-w-[1440px] mx-auto pb-12">
            {(activeTab === "overview" || activeTab === "dashboard") && (
              <OverviewTab
                analytics={analytics}
                health={health}
                setActiveTab={setActiveTab}
                onRefresh={refreshData}
                searchFilter={searchQuery}
              />
            )}
            {activeTab === "upload" && (
              <UploadTab onUploadSuccess={refreshData} setActiveTab={setActiveTab} />
            )}
            {activeTab === "queue" && (
              <ProcessingQueueTab setActiveTab={setActiveTab} />
            )}
            {activeTab === "review" && (
              <ReviewTab onReviewResolved={refreshData} />
            )}
            {activeTab === "students" && <StudentsTab />}
            {activeTab === "analytics" && (
              <AnalyticsTab analytics={analytics} loading={analyticsLoading} />
            )}
            {activeTab === "backlogs" && <BacklogsTab setActiveTab={setActiveTab} />}
            {activeTab === "export" && <ExportTab />}
            {activeTab === "history" && <HistoryTab />}
            {activeTab === "settings" && <SettingsTab onSettingsChanged={refreshData} />}
          </div>
        </main>
      </div>
    </div>
  );
}
