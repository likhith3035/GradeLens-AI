"use client";

import React, { useState, useEffect } from "react";
import {
  ShieldAlert,
  Search,
  AlertTriangle,
  FileSpreadsheet,
  Users,
  BookOpen
} from "lucide-react";
import { fetchStudents } from "../lib/api";
import { Student } from "../lib/types";

export default function BacklogsTab({ setActiveTab }: { setActiveTab: (tab: string) => void }) {
  const [backlogStudents, setBacklogStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    let ignore = false;
    void fetchStudents({
      has_backlogs: true,
      search: search || undefined,
      sort_by: "roll_number",
    })
      .then((data) => {
        if (!ignore) {
          setBacklogStudents(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load backlogs:", err);
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [search]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-800 tracking-tight flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-600" />
            Institutional Backlog Risk Analysis
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Verified tracking of students with uncleared course requirements and active semester failures.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Filter by roll no or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-3 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
            />
          </div>
          <button
            onClick={() => setActiveTab("export")}
            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5 shrink-0"
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            Export Backlogs Sheet
          </button>
        </div>
      </div>

      {/* Backlog Summary Box */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-red-200/80 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-red-50 text-red-600 flex items-center justify-center font-bold">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">{backlogStudents.length}</div>
            <div className="text-xs text-slate-500">Students with Active Backlogs</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-800">
              {backlogStudents.reduce((acc, st) => acc + st.total_backlogs, 0)}
            </div>
            <div className="text-xs text-slate-500">Total Failed Subject Instances</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-800">
              {backlogStudents.filter((st) => st.total_backlogs > 2).length}
            </div>
            <div className="text-xs text-slate-500">Critical Risk Students (&gt; 2 Backlogs)</div>
          </div>
        </div>
      </div>

      {/* Backlog Students Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">Scanning backlog records...</div>
        ) : backlogStudents.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-slate-800 text-sm">No Active Backlogs Detected</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
              Either all uploaded student records have cleared all subjects, or no records with failed subjects have been indexed yet.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Roll Number</th>
                  <th className="py-3 px-4">Student Name</th>
                  <th className="py-3 px-4">Branch</th>
                  <th className="py-3 px-4 text-center">Active Backlogs</th>
                  <th className="py-3 px-4 text-center">Current CGPA</th>
                  <th className="py-3 px-4 text-center">Risk Level</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {backlogStudents.map((st) => {
                  const isCritical = st.total_backlogs > 2;
                  return (
                    <tr key={st.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3 px-4 font-mono font-bold text-blue-700">{st.roll_number}</td>
                      <td className="py-3 px-4 font-semibold text-slate-800">{st.name}</td>
                      <td className="py-3 px-4 text-slate-600">{st.branch || "General"}</td>
                      <td className="py-3 px-4 text-center">
                        <span className="inline-block px-2.5 py-0.5 rounded-full font-bold bg-red-50 text-red-700 border border-red-200">
                          {st.total_backlogs} Subjects
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center font-bold text-slate-700">
                        {st.latest_cgpa !== null && st.latest_cgpa !== undefined ? st.latest_cgpa.toFixed(2) : "N/A"}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <span
                          className={`inline-block px-2 py-0.5 rounded-full font-bold text-[10px] uppercase ${
                            isCritical
                              ? "bg-red-600 text-white"
                              : "bg-amber-100 text-amber-800"
                          }`}
                        >
                          {isCritical ? "Critical Risk" : "Moderate Risk"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setActiveTab("students")}
                          className="text-blue-600 hover:underline font-semibold"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
