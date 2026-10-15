"use client";

import React, { useState, useEffect } from "react";
import {
  Settings,
  Server,
  Laptop,
  Cpu,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Database,
  Lock,
  Save,
  RotateCcw,
  Sparkles
} from "lucide-react";
import { fetchSettings, updateMode, updateTesseractPath, purgeData } from "../lib/api";
import { AppSettings } from "../lib/types";

interface SettingsTabProps {
  onSettingsChanged: () => void;
}

export default function SettingsTab({ onSettingsChanged }: SettingsTabProps) {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<"local" | "online">("local");
  const [tesseractPath, setTesseractPath] = useState("");
  const [savingTesseract, setSavingTesseract] = useState(false);
  const [purging, setPurging] = useState(false);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await fetchSettings();
      setSettings(data);
      setMode(data.mode);
      setTesseractPath(data.tesseract_cmd);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleModeChange = async (newMode: "local" | "online") => {
    try {
      await updateMode(newMode);
      setMode(newMode);
      loadSettings();
      onSettingsChanged();
      alert(`System switched to ${newMode === "local" ? "Local PC Mode" : "Online Cloud Mode"}.`);
    } catch (err: any) {
      alert(`Failed to update mode: ${err.message}`);
    }
  };

  const handleSaveTesseract = async () => {
    setSavingTesseract(true);
    try {
      const res = await updateTesseractPath(tesseractPath);
      alert(res.message);
      loadSettings();
      onSettingsChanged();
    } catch (err: any) {
      alert(`Error updating path: ${err.message}`);
    } finally {
      setSavingTesseract(false);
    }
  };

  const handlePurge = async () => {
    const confirm = window.confirm(
      "WARNING: This will permanently delete ALL student records, semester marks, recent processing documents, and uploaded files. Are you sure?"
    );
    if (!confirm) return;

    setPurging(true);
    try {
      await purgeData();
      alert("All student records, marks, recent processing files, and uploaded documents have been permanently purged.");
      onSettingsChanged();
    } catch (err: any) {
      alert(`Error purging data: ${err.message}`);
    } finally {
      setPurging(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#0c1524] text-white flex items-center justify-center shadow-xs">
            <Settings className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800 tracking-tight">
              Application Settings & Configuration
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Configure deployment modes, OCR binary paths, and data retention policies.
            </p>
          </div>
        </div>

        <button
          onClick={loadSettings}
          className="px-3.5 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1.5 cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* Mode Switcher */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
        <div>
          <h3 className="font-bold text-sm text-slate-800 mb-1">Operating Mode</h3>
          <p className="text-xs text-slate-500">
            Switch between Local Edge Execution (private zero-cloud computing) and Online Cloud Execution.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            onClick={() => handleModeChange("local")}
            className={`p-4 rounded-2xl border-2 transition-all cursor-pointer flex items-start gap-3.5 ${
              mode === "local"
                ? "border-emerald-500 bg-emerald-50/30 shadow-xs"
                : "border-slate-200 hover:border-slate-300 bg-white"
            }`}
          >
            <div className={`p-2.5 rounded-xl ${mode === "local" ? "bg-emerald-600 text-white" : "bg-slate-100 text-slate-500"}`}>
              <Laptop className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-xs text-slate-800">Local PC Mode (Edge)</span>
                {mode === "local" && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                    Active
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                Processes all PDF & image files locally using PyMuPDF and system Tesseract. Fully private and offline.
              </p>
            </div>
          </div>

          <div
            onClick={() => handleModeChange("online")}
            className={`p-4 rounded-2xl border-2 transition-all cursor-pointer flex items-start gap-3.5 ${
              mode === "online"
                ? "border-blue-500 bg-blue-50/30 shadow-xs"
                : "border-slate-200 hover:border-slate-300 bg-white"
            }`}
          >
            <div className={`p-2.5 rounded-xl ${mode === "online" ? "bg-blue-600 text-white" : "bg-slate-100 text-slate-500"}`}>
              <Server className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-xs text-slate-800">Online Cloud Mode</span>
                {mode === "online" && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                    Active
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                Connects to centralized cloud database and distributed queue workers for high-volume batches.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* OCR Configuration */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-slate-800 mb-1 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-emerald-500" />
              Tesseract OCR Engine Configuration
            </h3>
            <p className="text-xs text-slate-500">
              Scanned marks memo images and non-searchable PDFs rely on local Tesseract OCR.
            </p>
          </div>

          <span
            className={`px-3 py-1 rounded-full text-xs font-bold border ${
              settings?.tesseract_available
                ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                : "bg-amber-50 text-amber-700 border-amber-300"
            }`}
          >
            {settings?.tesseract_available ? "OCR Ready" : "OCR Not Detected"}
          </span>
        </div>

        <div>
          <label className="text-[11px] font-bold text-slate-600 mb-1.5 block">
            Tesseract Executable Path (Windows / Linux)
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={tesseractPath}
              onChange={(e) => setTesseractPath(e.target.value)}
              placeholder="C:\Program Files\Tesseract-OCR\tesseract.exe"
              className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs font-mono font-medium focus:outline-none focus:ring-1 focus:ring-emerald-500 text-slate-800"
            />
            <button
              onClick={handleSaveTesseract}
              disabled={savingTesseract}
              className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold shadow-xs transition-all flex items-center gap-1.5 shrink-0 cursor-pointer"
            >
              <Save className="w-3.5 h-3.5" />
              {savingTesseract ? "Testing..." : "Test & Save"}
            </button>
          </div>
          <p className="text-[11px] text-slate-500 mt-1.5">
            Windows default: <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">C:\Program Files\Tesseract-OCR\tesseract.exe</code>.
          </p>
        </div>
      </div>

      {/* Data Retention & Privacy Purge */}
      <div className="bg-white rounded-2xl p-6 border border-rose-200 shadow-xs space-y-4">
        <div>
          <h3 className="font-bold text-sm text-rose-600 mb-1 flex items-center gap-2">
            <Trash2 className="w-4 h-4" />
            User-Controlled Data Purge
          </h3>
          <p className="text-xs text-slate-500">
            Compliant with institutional privacy requirements. Clears all student records, marks memorandums, recent processing documents, and disk uploads.
          </p>
        </div>

        <button
          onClick={handlePurge}
          disabled={purging}
          className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-sm transition-all flex items-center gap-2 cursor-pointer"
        >
          <Trash2 className="w-4 h-4" />
          {purging ? "Purging Records..." : "Purge All Data & Uploaded Documents"}
        </button>
      </div>
    </div>
  );
}
