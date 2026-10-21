"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Users,
  Search,
  ArrowUpDown,
  ChevronRight,
  X,
  FileText,
  TrendingUp
} from "lucide-react";
import { fetchStudents, fetchStudentDetail, getDocumentFileUrl } from "../lib/api";
import { Student } from "../lib/types";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function StudentsTab() {
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedBranch, setSelectedBranch] = useState("");
  const [hasBacklogsOnly, setHasBacklogsOnly] = useState<boolean | undefined>(undefined);
  const [sortBy, setSortBy] = useState("roll_number");
  const [sortOrder, setSortOrder] = useState("asc");

  // Selected student for detailed profile modal/drawer
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);

  const loadStudents = useCallback(async () => {
    try {
      const data = await fetchStudents({
        search: search || undefined,
        branch: selectedBranch || undefined,
        has_backlogs: hasBacklogsOnly,
        sort_by: sortBy,
        sort_order: sortOrder,
      });
      setStudents(data);
    } catch (err) {
      console.error("Failed to load students:", err);
    } finally {
      setLoading(false);
    }
  }, [search, selectedBranch, hasBacklogsOnly, sortBy, sortOrder]);

  useEffect(() => {
    let ignore = false;
    void fetchStudents({
      search: search || undefined,
      branch: selectedBranch || undefined,
      has_backlogs: hasBacklogsOnly,
      sort_by: sortBy,
      sort_order: sortOrder,
    })
      .then((data) => {
        if (!ignore) {
          setStudents(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load students:", err);
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [search, selectedBranch, hasBacklogsOnly, sortBy, sortOrder]);

  const openStudentProfile = async (roll: string) => {
    try {
      const detail = await fetchStudentDetail(roll);
      setSelectedStudent(detail);
    } catch {
      alert("Failed to load student profile");
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-[#0c1524] text-white flex items-center justify-center shadow-xs">
              <Users className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-800 tracking-tight">
                Student Academic Directory
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Consolidated profiles linked by normalized roll number. View semester history, subjects, and backlogs.
              </p>
            </div>
          </div>

          <div className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-full">
            Showing {students.length} students
          </div>
        </div>

        {/* Filter controls */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
          {/* Search bar */}
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by name or roll no..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
            />
          </div>

          {/* Branch Filter */}
          <div>
            <select
              value={selectedBranch}
              onChange={(e) => setSelectedBranch(e.target.value)}
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

          {/* Backlog filter */}
          <div>
            <select
              value={hasBacklogsOnly === undefined ? "" : hasBacklogsOnly ? "backlog" : "clear"}
              onChange={(e) => {
                if (e.target.value === "backlog") setHasBacklogsOnly(true);
                else if (e.target.value === "clear") setHasBacklogsOnly(false);
                else setHasBacklogsOnly(undefined);
              }}
              className="w-full py-2 px-3 bg-slate-50 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            >
              <option value="">All Academic Standings</option>
              <option value="clear">All Clear (Zero Backlogs)</option>
              <option value="backlog">Has Active Backlogs</option>
            </select>
          </div>

          {/* Sort By */}
          <div className="flex items-center gap-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full py-2 px-3 bg-slate-50 border border-slate-300 rounded-lg text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-700"
            >
              <option value="roll_number">Sort by Roll Number</option>
              <option value="name">Sort by Student Name</option>
              <option value="cgpa">Sort by CGPA</option>
              <option value="created_at">Sort by Date Added</option>
            </select>
            <button
              onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
              className="p-2 border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-600 transition-colors"
              title="Toggle sort direction"
            >
              <ArrowUpDown className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Students Data Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-slate-400 text-sm">Loading student directory...</div>
        ) : students.length === 0 ? (
          <div className="p-12 text-center text-slate-400 text-sm">
            No students found matching current filters.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Roll Number</th>
                  <th className="py-3 px-4">Student Name</th>
                  <th className="py-3 px-4">Branch</th>
                  <th className="py-3 px-4">Batch</th>
                  <th className="py-3 px-4 text-center">Semesters</th>
                  <th className="py-3 px-4 text-center">CGPA</th>
                  <th className="py-3 px-4 text-center">Backlogs</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {students.map((st) => (
                  <tr
                    key={st.id}
                    onClick={() => openStudentProfile(st.roll_number)}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-blue-700">{st.roll_number}</td>
                    <td className="py-3 px-4 font-semibold text-slate-800">{st.name}</td>
                    <td className="py-3 px-4 text-slate-600">{st.branch || "General"}</td>
                    <td className="py-3 px-4 text-slate-500">{st.batch || "-"}</td>
                    <td className="py-3 px-4 text-center font-medium text-slate-700">{st.semesters_count}</td>
                    <td className="py-3 px-4 text-center">
                      <span className="inline-block px-2.5 py-0.5 rounded-full font-bold bg-blue-50 text-blue-700 border border-blue-200">
                        {st.latest_cgpa !== null && st.latest_cgpa !== undefined ? st.latest_cgpa.toFixed(2) : "N/A"}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full font-bold ${
                          st.total_backlogs === 0
                            ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                            : "bg-red-50 text-red-700 border border-red-200"
                        }`}
                      >
                        {st.total_backlogs === 0 ? "All Clear" : `${st.total_backlogs} Active`}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className="text-blue-600 font-semibold text-xs inline-flex items-center gap-1 hover:underline">
                        Profile <ChevronRight className="w-3.5 h-3.5" />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Student Profile Modal */}
      {selectedStudent && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] flex flex-col shadow-2xl border border-slate-200 overflow-hidden">
            {/* Modal Header */}
            <div className="p-6 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center font-bold text-lg">
                  {selectedStudent.name.charAt(0)}
                </div>
                <div>
                  <h3 className="font-bold text-lg leading-tight">{selectedStudent.name}</h3>
                  <div className="flex items-center gap-2 text-xs text-slate-300 font-mono mt-0.5">
                    <span>{selectedStudent.roll_number}</span>
                    <span>•</span>
                    <span>{selectedStudent.branch || "General"}</span>
                    {selectedStudent.batch && (
                      <>
                        <span>•</span>
                        <span>Batch {selectedStudent.batch}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedStudent(null)}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              {/* Summary Stats Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">Cumulative CGPA</div>
                  <div className="text-xl font-bold text-blue-700 mt-0.5">
                    {selectedStudent.latest_cgpa !== null && selectedStudent.latest_cgpa !== undefined ? selectedStudent.latest_cgpa.toFixed(2) : "N/A"}
                  </div>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">Total Semesters</div>
                  <div className="text-xl font-bold text-slate-800 mt-0.5">{selectedStudent.semesters_count}</div>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">Backlog Count</div>
                  <div className={`text-xl font-bold mt-0.5 ${selectedStudent.total_backlogs > 0 ? "text-red-600" : "text-emerald-600"}`}>
                    {selectedStudent.total_backlogs}
                  </div>
                </div>
                <div className="bg-slate-50 p-3 rounded-xl border border-slate-200">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">College</div>
                  <div className="text-xs font-medium text-slate-700 truncate mt-1">
                    {selectedStudent.college_name || "Autonomous Institution"}
                  </div>
                </div>
              </div>

              {/* Multi-Semester SGPA Progression Trajectory Chart */}
              {selectedStudent.semester_results && selectedStudent.semester_results.length > 1 && (
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-slate-800 text-xs uppercase tracking-wide flex items-center gap-1.5">
                      <TrendingUp className="w-4 h-4 text-blue-600" />
                      Multi-Semester Academic Trajectory (SGPA Curve)
                    </h4>
                    <span className="text-[11px] font-semibold text-blue-700 bg-blue-100/60 px-2 py-0.5 rounded">
                      {selectedStudent.semesters_count} Semesters Consolidated
                    </span>
                  </div>
                  <div className="h-40 w-full pt-2">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={selectedStudent.semester_results.map((s) => ({
                          semester: s.semester,
                          sgpa: s.sgpa,
                        }))}
                        margin={{ top: 5, right: 20, left: -20, bottom: 5 }}
                      >
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                        <XAxis dataKey="semester" tick={{ fontSize: 10 }} />
                        <YAxis domain={[0, 10]} tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="sgpa"
                          stroke="#2563EB"
                          strokeWidth={2.5}
                          dot={{ r: 4, fill: "#2563EB" }}
                          name="Semester SGPA"
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              )}

              {/* Semester History */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-slate-800 text-sm uppercase tracking-wide">
                    Semester Academic Records
                  </h4>
                  <span className="text-xs text-slate-400">
                    Chronologically linked by Hall Ticket / Roll Number
                  </span>
                </div>

                {selectedStudent.semester_results?.map((sem, idx) => (
                  <div key={idx} className="border border-slate-200 rounded-xl overflow-hidden shadow-sm bg-white">
                    <div className="bg-slate-100/70 px-4 py-2.5 flex flex-wrap items-center justify-between gap-2 border-b border-slate-200">
                      <div className="flex items-center gap-3">
                        <span className="font-bold text-xs text-slate-800">
                          Semester: {sem.semester}
                        </span>
                        {sem.examination_name && (
                          <span className="text-[11px] text-slate-500">
                            {sem.examination_name} ({sem.examination_month_year || ""})
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className="font-medium text-slate-600">
                          SGPA: <strong className="text-blue-700">{sem.sgpa ?? "N/A"}</strong>
                        </span>
                        <span className="font-medium text-slate-600">
                          Credits: <strong>{sem.total_credits ?? "N/A"}</strong>
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
                            sem.backlog_count === 0
                              ? "bg-emerald-100 text-emerald-800"
                              : "bg-red-100 text-red-800"
                          }`}
                        >
                          {sem.backlog_count === 0 ? "PASSED" : `${sem.backlog_count} BACKLOGS`}
                        </span>
                        {sem.document_id && (
                          <a
                            href={getDocumentFileUrl(sem.document_id)}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[11px] font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-2.5 py-0.5 rounded border border-blue-200 transition-colors flex items-center gap-1"
                          >
                            <FileText className="w-3 h-3" />
                            View Memo PDF ↗
                          </a>
                        )}
                      </div>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-50 text-slate-500 border-b border-slate-200">
                          <tr>
                            <th className="py-2 px-3">Code</th>
                            <th className="py-2 px-3">Subject Name</th>
                            <th className="py-2 px-2 text-center">Int</th>
                            <th className="py-2 px-2 text-center">Ext</th>
                            <th className="py-2 px-2 text-center">Total</th>
                            <th className="py-2 px-2 text-center">Grade</th>
                            <th className="py-2 px-2 text-center">Credits</th>
                            <th className="py-2 px-2 text-center">Result</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {sem.subject_marks.map((sub, sIdx) => (
                            <tr
                              key={sIdx}
                              className={`hover:bg-slate-50/50 ${!sub.is_pass ? "bg-red-50/40 text-red-900" : ""}`}
                            >
                              <td className="py-2 px-3 font-mono font-medium">{sub.subject_code}</td>
                              <td className="py-2 px-3 font-medium">{sub.subject_name}</td>
                              <td className="py-2 px-2 text-center text-slate-500">{sub.internal_marks ?? "-"}</td>
                              <td className="py-2 px-2 text-center text-slate-500">{sub.external_marks ?? "-"}</td>
                              <td className="py-2 px-2 text-center font-bold">{sub.total_marks ?? "-"}</td>
                              <td className="py-2 px-2 text-center font-bold">{sub.grade || "-"}</td>
                              <td className="py-2 px-2 text-center">{sub.credits ?? "-"}</td>
                              <td className="py-2 px-2 text-center">
                                <span
                                  className={`px-1.5 py-0.5 rounded font-bold text-[10px] ${
                                    sub.is_pass ? "bg-emerald-100 text-emerald-800" : "bg-red-100 text-red-800"
                                  }`}
                                >
                                  {sub.subject_result || (sub.is_pass ? "P" : "F")}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => setSelectedStudent(null)}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold shadow-sm transition-colors"
              >
                Close Profile
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
