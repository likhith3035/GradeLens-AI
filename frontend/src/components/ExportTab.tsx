"use client";

import React, { useState } from "react";
import {
  FileSpreadsheet,
  Download,
  Filter,
  CheckCircle2,
  Layers
} from "lucide-react";
import { getExcelExportUrl } from "../lib/api";

export default function ExportTab() {
  const [branch, setBranch] = useState("");
  const [batch, setBatch] = useState("");
  const [semester, setSemester] = useState("");
  const [verifiedOnly, setVerifiedOnly] = useState(false);
  const [rollNumbers, setRollNumbers] = useState("");
  const [downloading, setDownloading] = useState(false);

  const handleDownload = () => {
    setDownloading(true);
    const url = getExcelExportUrl({
      branch: branch || undefined,
      batch: batch || undefined,
      semester: semester || undefined,
      verified_only: verifiedOnly,
      roll_numbers: rollNumbers || undefined,
    });

    window.open(url, "_blank");
    setTimeout(() => setDownloading(false), 2000);
  };

  const sheets = [
    {
      num: 1,
      title: "Student Details",
      desc: "One row per student per semester: Name, Roll Number, College, Branch, SGPA, CGPA, Backlogs, Result, and Verification Status.",
      badge: "Institutional Record",
    },
    {
      num: 2,
      title: "Subject Marks",
      desc: "One row per student per subject: Roll Number, Subject Code, Subject Name, Internals, Externals, Totals, Grades, Points, Credits, Pass/Fail.",
      badge: "Granular Course Data",
    },
    {
      num: 3,
      title: "Backlogs",
      desc: "Strictly verified active failures and uncleared backlog requirements with failure course titles and subject codes.",
      badge: "Remedial Tracking",
    },
    {
      num: 4,
      title: "KPI Summary",
      desc: "Institutional summary metrics, pass percentages, average CGPA, and branch-by-branch aggregated academic performance.",
      badge: "Executive Analytics",
    },
    {
      num: 5,
      title: "Processing Issues",
      desc: "Audit trail of document issues, missing mandatory fields, low OCR confidence warnings, and calculation mismatch notes.",
      badge: "Data Integrity & Audit",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-800 tracking-tight flex items-center gap-2">
            <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
            Consolidated Excel Export Center
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Generates standardized .xlsx workbooks with formatted tables, frozen headers, formula-injection guards, and text-safe roll numbers.
          </p>
        </div>

        <button
          onClick={handleDownload}
          disabled={downloading}
          className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-md shadow-emerald-600/20 transition-all flex items-center gap-2"
        >
          <Download className="w-4 h-4" />
          {downloading ? "Preparing Workbook..." : "Download Consolidated Excel (.xlsx)"}
        </button>
      </div>

      {/* Filter Configuration Card */}
      <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
          <Filter className="w-4 h-4 text-blue-600" />
          Export Scope & Filter Controls
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label className="text-[11px] font-bold text-slate-600 mb-1 block">Filter by Branch</label>
            <select
              value={branch}
              onChange={(e) => setBranch(e.target.value)}
              className="w-full py-2 px-3 bg-slate-50 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            >
              <option value="">All Branches</option>
              <option value="COMPUTER SCIENCE AND ENGINEERING">Computer Science & Engineering</option>
              <option value="ELECTRONICS & COMMUNICATION ENGINEERING">ECE</option>
              <option value="MECHANICAL ENGINEERING">Mechanical</option>
              <option value="CIVIL ENGINEERING">Civil</option>
              <option value="INFORMATION TECHNOLOGY">IT</option>
            </select>
          </div>

          <div>
            <label className="text-[11px] font-bold text-slate-600 mb-1 block">Filter by Semester</label>
            <input
              type="text"
              placeholder="e.g. III-II or VI"
              value={semester}
              onChange={(e) => setSemester(e.target.value)}
              className="w-full py-2 px-3 bg-slate-50 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            />
          </div>

          <div>
            <label className="text-[11px] font-bold text-slate-600 mb-1 block">Filter by Batch</label>
            <input
              type="text"
              placeholder="e.g. 2020-2024"
              value={batch}
              onChange={(e) => setBatch(e.target.value)}
              className="w-full py-2 px-3 bg-slate-50 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            />
          </div>
        </div>

        <div>
          <label className="text-[11px] font-bold text-slate-600 mb-1 block">
            Specific Roll Numbers (optional, comma-separated)
          </label>
          <input
            type="text"
            placeholder="e.g. 20671A0512, 20671A0545, 312218104001"
            value={rollNumbers}
            onChange={(e) => setRollNumbers(e.target.value)}
            className="w-full py-2 px-3 bg-slate-50 border border-slate-300 rounded-lg text-xs font-mono font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
          />
        </div>

        <div className="flex items-center gap-2 pt-1">
          <input
            type="checkbox"
            id="verifiedOnly"
            checked={verifiedOnly}
            onChange={(e) => setVerifiedOnly(e.target.checked)}
            className="rounded text-blue-600 focus:ring-blue-500"
          />
          <label htmlFor="verifiedOnly" className="text-xs text-slate-700 font-medium cursor-pointer">
            Export verified records only (exclude records currently awaiting manual review)
          </label>
        </div>
      </div>

      {/* 5-Sheet Architecture Preview */}
      <div className="space-y-3">
        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Layers className="w-4 h-4 text-indigo-600" />
          Workbook Architecture (5 Standardized Sheets)
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sheets.map((s) => (
            <div
              key={s.num}
              className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-xs text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                    Sheet {s.num}
                  </span>
                  <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                    {s.badge}
                  </span>
                </div>
                <h4 className="font-bold text-slate-800 text-sm mb-1">{s.title}</h4>
                <p className="text-xs text-slate-500 leading-relaxed">{s.desc}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-1.5 text-[11px] text-emerald-600 font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Formatted & Text-Preserved
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
