"use client";

import React, { useState, useEffect } from "react";
import {
  Clock,
  ShieldCheck,
  RotateCcw,
  User,
  Calendar,
  Activity,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { fetchAuditLogs } from "../lib/api";

export default function HistoryTab() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await fetchAuditLogs(50);
      setLogs(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#0c1524] text-white flex items-center justify-center shadow-xs">
            <Clock className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800 tracking-tight">Audit Trail & Verification History</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Immutable logging of reviewer overrides, marks corrections, batch deletions, and system events.
            </p>
          </div>
        </div>

        <button
          onClick={loadLogs}
          className="px-3.5 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1.5"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {/* History Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading audit history...</div>
        ) : logs.length === 0 ? (
          <div className="p-12 text-center">
            <ShieldCheck className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
            <h3 className="text-sm font-bold text-slate-800">System Logs Clean</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              Any manual mark edits, status overrides, or student profile updates will be recorded here with user attribution.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/70 border-b border-slate-200/60 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-5">Timestamp</th>
                  <th className="py-3 px-5">Actor</th>
                  <th className="py-3 px-5">Entity</th>
                  <th className="py-3 px-5">Action</th>
                  <th className="py-3 px-5">Field Changed</th>
                  <th className="py-3 px-5">Previous Value</th>
                  <th className="py-3 px-5">New Value</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3.5 px-5 text-slate-500 font-mono text-[11px]">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : "—"}
                    </td>
                    <td className="py-3.5 px-5 font-semibold text-slate-800 flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      {log.actor}
                    </td>
                    <td className="py-3.5 px-5 font-medium text-slate-700">
                      {log.entity_type} #{log.entity_id}
                    </td>
                    <td className="py-3.5 px-5">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3.5 px-5 font-mono text-slate-700">{log.field_name || "—"}</td>
                    <td className="py-3.5 px-5 text-rose-600 line-through max-w-xs truncate">
                      {log.old_value || "—"}
                    </td>
                    <td className="py-3.5 px-5 text-emerald-600 font-semibold max-w-xs truncate">
                      {log.new_value || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
