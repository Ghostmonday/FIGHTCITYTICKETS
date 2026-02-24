"use client";

import { useState, useEffect } from "react";
import { error as logError } from "../../lib/logger";

const API_URL = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

interface IntakeDetail {
  id: number;
  created_at: string;
  citation_number: string;
  status: string;
  user_name: string;
  user_email?: string;
  user_phone?: string;
  user_address: string;
  violation_date?: string;
  vehicle_info?: string;
  draft_text?: string;
  payment_status?: string;
  amount_total?: number;
  lob_tracking_id?: string;
  lob_mail_type?: string;
  is_fulfilled: boolean;
}

export default function AdminPage() {
  const [adminKey, setAdminKey] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [activeTab, setActiveTab] = useState("dashboard");
  const [stats, setStats] = useState<any>(null);
  const [activity, setActivity] = useState<any[]>([]);
  const [logs, setLogs] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Detail Modal State
  const [selectedIntakeId, setSelectedIntakeId] = useState<number | null>(null);
  const [detailData, setDetailData] = useState<IntakeDetail | null>(null);

  // Check authentication on load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch(`${API_URL}/admin/me`, {
          credentials: "include",
        });
        if (res.ok) {
          setIsAuthenticated(true);
        }
      } catch (err) {
        // Not authenticated, stay on login screen
      }
    };
    checkAuth();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (adminKey.trim()) {
      setLoading(true);
      setError("");
      try {
        const res = await fetch(`${API_URL}/admin/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ secret: adminKey }),
          credentials: "include",
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || "Authentication failed");
        }

        setIsAuthenticated(true);
        setAdminKey(""); // Clear secret from state
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/admin/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (e) {
      logError("Logout failed", e);
    } finally {
      setIsAuthenticated(false);
      setActiveTab("dashboard");
    }
  };

  const fetchStats = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_URL}/admin/stats`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Authentication failed or server error");
      const data = await res.json();
      setStats(data);
    } catch (err: any) {
      setError(err.message);
      if (err.message.includes("Authentication")) setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const fetchActivity = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/admin/activity`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to fetch activity");
      const data = await res.json();
      setActivity(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/admin/logs?lines=200`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to fetch logs");
      const data = await res.json();
      setLogs(data.logs);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDetail = async (id: number) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/admin/intake/${id}`, {
        credentials: "include",
      });
      if (!res.ok) throw new Error("Failed to fetch details");
      const data = await res.json();
      setDetailData(data);
      setSelectedIntakeId(id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const closeDetail = () => {
    setSelectedIntakeId(null);
    setDetailData(null);
  };

  useEffect(() => {
    if (isAuthenticated) {
      if (activeTab === "dashboard") fetchStats();
      if (activeTab === "activity") fetchActivity();
      if (activeTab === "logs") fetchLogs();
    }
  }, [isAuthenticated, activeTab]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded shadow-lg w-full max-w-md">
          <h1 className="text-2xl font-bold mb-6 text-center">
            Server Access Panel
          </h1>
          <form onSubmit={handleLogin}>
            <input
              type="password"
              placeholder="Enter Admin Secret Key"
              className="w-full p-3 border rounded mb-4 text-gray-900"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              disabled={loading}
            />
            {error && <p className="text-red-500 mb-4">{error}</p>}
            <button
              type="submit"
              className="w-full bg-indigo-600 text-white p-3 rounded hover:bg-indigo-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? "Authenticating..." : "Access Server"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-indigo-600">
            Server Access Panel
          </h1>
          <div className="space-x-4">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-3 py-2 rounded ${
                activeTab === "dashboard"
                  ? "bg-indigo-100 text-indigo-700"
                  : "text-gray-600"
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setActiveTab("activity")}
              className={`px-3 py-2 rounded ${
                activeTab === "activity"
                  ? "bg-indigo-100 text-indigo-700"
                  : "text-gray-600"
              }`}
            >
              Activity
            </button>
            <button
              onClick={() => setActiveTab("logs")}
              className={`px-3 py-2 rounded ${
                activeTab === "logs"
                  ? "bg-indigo-100 text-indigo-700"
                  : "text-gray-600"
              }`}
            >
              Logs
            </button>
            <button
              onClick={handleLogout}
              className="px-3 py-2 text-red-600 hover:bg-red-50 rounded"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 py-8 relative">
        {loading && <div className="text-center py-4">Loading...</div>}

        {/* Detail Modal */}
        {selectedIntakeId && detailData && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
            <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">
                  Appeal Details #{detailData.id}
                </h2>
                <button
                  onClick={closeDetail}
                  className="text-gray-500 hover:text-gray-700 text-xl font-bold"
                >
                  ✕
                </button>
              </div>

              <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Left Column: User & Status */}
                <div className="space-y-6">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3 text-indigo-700">
                      👤 User Details
                    </h3>
                    <div className="space-y-2 text-sm">
                      <p>
                        <span className="font-medium">Name:</span>{" "}
                        {detailData.user_name}
                      </p>
                      <p>
                        <span className="font-medium">Email:</span>{" "}
                        {detailData.user_email || "N/A"}
                      </p>
                      <p>
                        <span className="font-medium">Address:</span>
                      </p>
                      <p className="whitespace-pre-line pl-4 text-gray-600">
                        {detailData.user_address}
                      </p>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3 text-indigo-700">
                      🚗 Appeal Info
                    </h3>
                    <div className="space-y-2 text-sm">
                      <p>
                        <span className="font-medium">Citation #:</span>{" "}
                        {detailData.citation_number}
                      </p>
                      <p>
                        <span className="font-medium">Violation Date:</span>{" "}
                        {detailData.violation_date}
                      </p>
                      <p>
                        <span className="font-medium">Vehicle:</span>{" "}
                        {detailData.vehicle_info}
                      </p>
                      <p>
                        <span className="font-medium">Status:</span>{" "}
                        {detailData.status}
                      </p>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3 text-indigo-700">
                      📦 Mail Tracking (Lob)
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">Status:</span>
                        <span
                          className={`px-2 py-1 rounded text-xs font-bold ${
                            detailData.is_fulfilled
                              ? "bg-green-100 text-green-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {detailData.is_fulfilled
                            ? "MAILED / FULFILLED"
                            : "PENDING"}
                        </span>
                      </div>
                      {detailData.lob_tracking_id ? (
                        <div className="mt-2 p-2 bg-white border rounded">
                          <p className="font-mono text-xs text-gray-600">
                            Tracking ID: {detailData.lob_tracking_id}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Carrier:{" "}
                            {detailData.lob_mail_type === "usps_certified"
                              ? "USPS Certified"
                              : "USPS Standard"}
                          </p>
                        </div>
                      ) : (
                        <p className="text-gray-500 italic">
                          No tracking information available yet.
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Right Column: Letter */}
                <div>
                  <h3 className="text-lg font-semibold mb-3 text-indigo-700">
                    📝 Appeal Letter
                  </h3>
                  <div className="bg-gray-50 p-4 rounded-lg border h-96 overflow-y-auto font-mono text-xs whitespace-pre-wrap">
                    {detailData.draft_text || "No draft text available."}
                  </div>
                </div>
              </div>

              <div className="p-6 border-t bg-gray-50 flex justify-end">
                <button
                  onClick={closeDetail}
                  className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded text-gray-800 font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Dashboard Tab */}
        {activeTab === "dashboard" && stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded shadow">
              <h3 className="text-gray-500 text-sm font-medium">
                Total Intakes
              </h3>
              <p className="text-3xl font-bold text-gray-900">
                {stats.total_intakes}
              </p>
            </div>
            <div className="bg-white p-6 rounded shadow">
              <h3 className="text-gray-500 text-sm font-medium">
                Total Drafts
              </h3>
              <p className="text-3xl font-bold text-gray-900">
                {stats.total_drafts}
              </p>
            </div>
            <div className="bg-white p-6 rounded shadow">
              <h3 className="text-gray-500 text-sm font-medium">
                Letters Mailed
              </h3>
              <p className="text-3xl font-bold text-green-600">
                {stats.fulfilled_count}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Successfully sent via Lob
              </p>
            </div>
            <div className="bg-white p-6 rounded shadow">
              <h3 className="text-gray-500 text-sm font-medium">
                Pending Fulfillments
              </h3>
              <p className="text-3xl font-bold text-indigo-600">
                {stats.pending_fulfillments}
              </p>
              <p className="text-xs text-gray-500 mt-1">Paid but not mailed</p>
            </div>
            <div className="bg-white p-6 rounded shadow col-span-1 md:col-span-4">
              <h3 className="text-gray-500 text-sm font-medium">
                Database Status
              </h3>
              <p
                className={`text-lg font-bold ${stats.db_status === "connected" ? "text-green-600" : "text-red-600"}`}
              >
                {stats.db_status.toUpperCase()}
              </p>
            </div>
          </div>
        )}

        {/* Activity Tab */}
        {activeTab === "activity" && (
          <div className="bg-white rounded shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Citation
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Mail
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {activity.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {item.citation_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        {item.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {item.lob_tracking_id ? (
                        <span className="text-green-600 font-medium text-xs">
                          MAILED
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => fetchDetail(item.id)}
                        className="text-indigo-600 hover:text-indigo-900 bg-indigo-50 px-3 py-1 rounded"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Logs Tab */}
        {activeTab === "logs" && (
          <div className="bg-gray-900 text-gray-100 rounded shadow p-4 font-mono text-sm h-[600px] overflow-auto whitespace-pre-wrap">
            {logs ||
              "No logs available or server has not written to log file yet."}
          </div>
        )}
      </main>
    </div>
  );
}
