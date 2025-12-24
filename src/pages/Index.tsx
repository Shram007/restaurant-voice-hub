import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/dashboard/StatCard";
import { StatusIndicator } from "@/components/dashboard/StatusIndicator";
import { Button } from "@/components/ui/button";
import { api } from "@/services/api";
import {
  Phone,
  ShoppingBag,
  DollarSign,
  TrendingUp,
  Link as LinkIcon,
  Upload,
  ArrowRight,
  Mic,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useVoiceAgent } from "@/hooks/use-voice-agent";

const Index = () => {
  const [stats, setStats] = useState<any>(null);
  const [recentOrders, setRecentOrders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const { status, isSpeaking, startConversation, stopConversation } = useVoiceAgent();
  const isConnected = status === "connected";

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsData, ordersData] = await Promise.all([
          api.getStats(),
          api.getOrders("today")
        ]);
        setStats(statsData);
        setRecentOrders(ordersData.slice(0, 3));
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <DashboardLayout
      title="Dashboard"
      subtitle="Welcome back! Here's what's happening with your AI assistant."
    >
      <div className="space-y-8">
        {/* AI Status Card */}
        <div className="bg-card rounded-2xl border p-6 shadow-card animate-slide-up">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-primary/10">
                <Mic className="w-7 h-7 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-foreground">
                  AI Voice Assistant
                </h2>
                <StatusIndicator
                  status={stats?.aiStatus ?? "online"}
                  label={stats?.aiStatus === "online" ? "Online & Ready" : "Offline"}
                  size="sm"
                />
              </div>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button
                variant={isConnected ? "destructive" : "default"}
                onClick={isConnected ? stopConversation : startConversation}
                className="min-w-[140px]"
              >
                {isConnected ? (
                  <>
                    <Mic className="w-4 h-4 mr-2 animate-pulse" />
                    User Connected
                  </>
                ) : (
                  <>
                    <Phone className="w-4 h-4 mr-2" />
                    Connect Agent
                  </>
                )}
              </Button>
              <Button variant="outline" asChild>
                <Link to="/setup">
                  <LinkIcon className="w-4 h-4" />
                  Connect POS
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link to="/menu">
                  <Upload className="w-4 h-4" />
                  Upload Menu
                </Link>
              </Button>
              <Button asChild>
                <Link to="/orders">
                  View Orders
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Calls Today"
            value={stats?.callsToday ?? 0}
            icon={<Phone className="w-5 h-5" />}
            trend={{ value: 12, isPositive: true }}
            variant="primary"
          />
          <StatCard
            title="Orders Placed"
            value={stats?.ordersToday ?? 0}
            icon={<ShoppingBag className="w-5 h-5" />}
            trend={{ value: 8, isPositive: true }}
            variant="success"
          />
          <StatCard
            title="Today's Revenue"
            value={`$${(stats?.revenue ?? 0).toLocaleString()}`}
            icon={<DollarSign className="w-5 h-5" />}
            trend={{ value: 15, isPositive: true }}
          />
          <StatCard
            title="Conversion Rate"
            value={`${stats?.conversionRate?.toFixed(0) ?? 0}%`}
            icon={<TrendingUp className="w-5 h-5" />}
            subtitle="Calls → Orders"
          />
        </div>

        {/* Recent Orders */}
        <div className="bg-card rounded-2xl border shadow-card animate-slide-up">
          <div className="flex items-center justify-between p-5 border-b border-border">
            <h3 className="font-semibold text-foreground">Recent Orders</h3>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/orders">
                View All
                <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </div>
          <div className="divide-y divide-border">
            {recentOrders.map((order) => (
              <div
                key={order.id}
                className="flex items-center justify-between p-5 hover:bg-muted/50 transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <p className="font-medium text-foreground">
                      {order.customer_name}
                    </p>
                    <span className="text-xs text-muted-foreground">
                      {order.id}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground truncate">
                    {order.items}
                  </p>
                </div>
                <div className="flex items-center gap-4 ml-4">
                  <div className="text-right">
                    <p className="font-semibold text-foreground">
                      ${order.total.toFixed(2)}
                    </p>
                    <p className="text-xs text-muted-foreground">{order.eta}</p>
                  </div>
                  <span
                    className={`px-2.5 py-1 rounded-full text-xs font-medium ${order.status === "confirmed"
                        ? "bg-primary/10 text-primary"
                        : order.status === "in_progress"
                          ? "bg-warning/10 text-warning"
                          : "bg-success/10 text-success"
                      }`}
                  >
                    {order.status === "in_progress"
                      ? "In Progress"
                      : order.status.charAt(0).toUpperCase() +
                      order.status.slice(1)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/calls"
            className="group bg-card rounded-2xl border p-5 shadow-card hover:shadow-card-hover transition-all duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-secondary group-hover:bg-primary/10 transition-colors">
                <Phone className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Call Logs</p>
                <p className="text-sm text-muted-foreground">View AI insights</p>
              </div>
            </div>
          </Link>

          <Link
            to="/menu"
            className="group bg-card rounded-2xl border p-5 shadow-card hover:shadow-card-hover transition-all duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-secondary group-hover:bg-primary/10 transition-colors">
                <Upload className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Menu & FAQs</p>
                <p className="text-sm text-muted-foreground">Manage content</p>
              </div>
            </div>
          </Link>

          <Link
            to="/settings"
            className="group bg-card rounded-2xl border p-5 shadow-card hover:shadow-card-hover transition-all duration-200"
          >
            <div className="flex items-center gap-4">
              <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-secondary group-hover:bg-primary/10 transition-colors">
                <LinkIcon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Settings</p>
                <p className="text-sm text-muted-foreground">Configure AI</p>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Index;
