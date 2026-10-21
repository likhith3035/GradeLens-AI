"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from "recharts";
import {
  BarChart3,
  TrendingUp,
  Award,
  PieChart as PieIcon
} from "lucide-react";
import { AnalyticsFull } from "../lib/types";

interface AnalyticsTabProps {
  analytics: AnalyticsFull | null;
  loading: boolean;
}

export default function AnalyticsTab({ analytics, loading }: AnalyticsTabProps) {
  if (loading || !analytics) {
    return (
      <div className="bg-white rounded-xl p-12 border border-slate-200 text-center text-slate-400 text-sm">
        Loading analytics engine...
      </div>
    );
  }

  const { overview, branch_performance, semester_performance, grade_distribution } = analytics;

  if (overview.total_students === 0) {
    return (
      <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center max-w-lg mx-auto my-12">
        <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-4">
          <BarChart3 className="w-8 h-8" />
        </div>
        <h3 className="font-bold text-slate-800 text-lg mb-1">No Academic Records Available</h3>
        <p className="text-xs text-slate-500 mb-6">
          Upload student marks memos to instantly generate branch comparisons, grade distributions, pass/fail ratios, and CGPA trends.
        </p>
      </div>
    );
  }

  const passFailData = [
    { name: "Passed Subjects", value: overview.total_passed_records },
    { name: "Failed / Backlogs", value: overview.total_failed_records },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-5 border border-slate-200/80 shadow-sm flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-800 tracking-tight flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-indigo-600" />
            Institutional Academic Analytics
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Statistical breakdown computed directly from {overview.total_memos_processed} marks memos and {overview.total_subject_records} subject records.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <span className="font-semibold text-slate-600">Processing Success Rate:</span>
          <span className="font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
            {overview.processing_success_rate}%
          </span>
        </div>
      </div>

      {/* Top Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pass vs Fail Donut */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <PieIcon className="w-4 h-4 text-blue-600" />
              Overall Subject Pass Ratio
            </h3>
            <span className="text-xs font-bold text-emerald-600">{overview.overall_pass_rate}% Pass</span>
          </div>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={passFailData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  <Cell fill="#10B981" />
                  <Cell fill="#EF4444" />
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="pt-2 border-t border-slate-100 text-xs text-slate-500 flex justify-between">
            <span>Passed: {overview.total_passed_records}</span>
            <span>Backlogs: {overview.total_failed_records}</span>
          </div>
        </div>

        {/* Grade Distribution Bar */}
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <Award className="w-4 h-4 text-amber-500" />
              Grade Frequency Distribution
            </h3>
            <span className="text-xs text-slate-400">Total grades recorded: {overview.total_subject_records}</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={grade_distribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="grade" stroke="#64748B" fontSize={12} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={12} tickLine={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563EB" radius={[4, 4, 0, 0]} name="Occurrences" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Branch Performance Comparison */}
      {branch_performance.length > 0 && (
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-indigo-600" />
              Branch-wise Pass Rate & Academic Standings
            </h3>
          </div>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={branch_performance}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="branch" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={12} unit="%" domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="pass_rate" fill="#1E3A8A" name="Pass Rate (%)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Semester GPA Trend */}
      {semester_performance.length > 0 && (
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-800 text-sm flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-emerald-600" />
              Semester-wise Average SGPA & Pass Trends
            </h3>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={semester_performance}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="semester" stroke="#64748B" fontSize={12} />
                <YAxis stroke="#64748B" fontSize={12} domain={[0, 10]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="avg_sgpa" stroke="#2563EB" strokeWidth={3} name="Average SGPA" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
