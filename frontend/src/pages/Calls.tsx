import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/dashboard/StatCard";
import { api } from "@/services/api";
import {
  Phone,
  TrendingUp,
  Clock,
  AlertTriangle,
  PhoneForwarded,
  MessageSquare,
  ShoppingBag,
} from "lucide-react";
import { format } from "date-fns";

const Calls = () => {
  const [calls, setCalls] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [callsData, statsData] = await Promise.all([
          api.getCalls("today"),
          api.getStats()
        ]);
        setCalls(callsData);
        setStats(statsData);
      } catch (error) {
        console.error("Error fetching calls:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <DashboardLayout
      title="Call Logs & Insights"
      subtitle="Monitor AI performance and call outcomes."
    >
      <div className="space-y-6">
        {/* Insights */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Conversion Rate"
            value={`${stats?.conversionRate?.toFixed(0) ?? 0}%`}
            subtitle="Calls → Orders"
            icon={<TrendingUp className="w-5 h-5" />}
            variant="success"
          />
          <StatCard
            title="Avg Duration"
            value={stats?.avgCallDuration ?? "0:00"}
            icon={<Clock className="w-5 h-5" />}
          />
          <StatCard
            title="Fallback Rate"
            value={`${stats?.fallbackRate ?? 0}%`}
            subtitle="Transferred to human"
            icon={<AlertTriangle className="w-5 h-5" />}
            variant="warning"
          />
          <StatCard
            title="Total Calls"
            value={stats?.callsToday ?? 0}
            subtitle="Today"
            icon={<Phone className="w-5 h-5" />}
            variant="primary"
          />
        </div>

        {/* Call Logs Table */}
        <div className="bg-card rounded-2xl border shadow-card overflow-hidden">
          <div className="p-5 border-b border-border">
            <h3 className="font-semibold text-foreground">Recent Calls</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground">
                    Call ID
                  </th>
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground hidden sm:table-cell">
                    Phone
                  </th>
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground">
                    Duration
                  </th>
                  <th className="text-center px-5 py-4 text-sm font-semibold text-foreground">
                    Outcome
                  </th>
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground hidden md:table-cell">
                    Transfer Reason
                  </th>
                  <th className="text-right px-5 py-4 text-sm font-semibold text-foreground">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="text-center py-10 text-muted-foreground">
                      Loading calls...
                    </td>
                  </tr>
                ) : calls.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-10 text-muted-foreground">
                      No calls found.
                    </td>
                  </tr>
                ) : (
                  calls.map((call) => (
                    <tr
                      key={call.id}
                      className="hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-5 py-4">
                        <span className="font-mono text-sm text-foreground">
                          {call.id}
                        </span>
                      </td>
                      <td className="px-5 py-4 hidden sm:table-cell">
                        <span className="text-sm text-muted-foreground">
                          {call.phone}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm text-foreground">
                          {call.duration}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-center">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                            call.outcome === "order"
                              ? "bg-success/10 text-success"
                              : call.outcome === "faq"
                              ? "bg-primary/10 text-primary"
                              : "bg-warning/10 text-warning"
                          }`}
                        >
                          {call.outcome === "order" && (
                            <ShoppingBag className="w-3 h-3" />
                          )}
                          {call.outcome === "faq" && (
                            <MessageSquare className="w-3 h-3" />
                          )}
                          {call.outcome === "transferred" && (
                            <PhoneForwarded className="w-3 h-3" />
                          )}
                          {call.outcome === "transferred"
                            ? "Transferred"
                            : (call.outcome || "").toUpperCase()}
                        </span>
                      </td>
                      <td className="px-5 py-4 hidden md:table-cell">
                        <span className="text-sm text-muted-foreground">
                          {call.transfer_reason || "—"}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-right">
                        <span className="text-sm text-muted-foreground">
                          {format(new Date(call.timestamp), "h:mm a")}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Calls;
