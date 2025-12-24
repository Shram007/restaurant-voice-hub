import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { StatCard } from "@/components/dashboard/StatCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api } from "@/services/api";
import {
  ShoppingBag,
  DollarSign,
  TrendingUp,
  Search,
  Calendar,
  Filter,
} from "lucide-react";

type FilterType = "today" | "week" | "month" | "year" | "custom";

const Orders = () => {
  const [filter, setFilter] = useState<FilterType>("today");
  const [searchQuery, setSearchQuery] = useState("");
  const [orders, setOrders] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [ordersData, statsData] = await Promise.all([
          api.getOrders(filter),
          api.getStats()
        ]);
        setOrders(ordersData);
        setStats(statsData);
      } catch (error) {
        console.error("Error fetching orders:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [filter]);

  const filteredOrders = orders.filter(
    (order) =>
      order.customer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <DashboardLayout
      title="Orders"
      subtitle="Track and manage all orders placed through your AI assistant."
    >
      <div className="space-y-6">
        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            title="Total Orders"
            value={stats?.ordersToday ?? 0}
            icon={<ShoppingBag className="w-5 h-5" />}
            variant="success"
          />
          <StatCard
            title="Revenue"
            value={`$${(stats?.revenue ?? 0).toLocaleString()}`}
            icon={<DollarSign className="w-5 h-5" />}
          />
          <StatCard
            title="Avg Order Value"
            value={`$${(stats?.avgOrderValue ?? 0).toFixed(2)}`}
            icon={<TrendingUp className="w-5 h-5" />}
          />
          <StatCard
            title="Platform Commission"
            value={`$${((stats?.revenue ?? 0) * 0.1).toFixed(2)}`}
            subtitle="10% (Est.)"
            icon={<DollarSign className="w-5 h-5" />}
            variant="warning"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search orders..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="flex gap-2">
            {(["today", "week", "month", "year"] as FilterType[]).map((f) => (
              <Button
                key={f}
                variant={filter === f ? "default" : "outline"}
                size="sm"
                onClick={() => setFilter(f)}
              >
                {f === "today" ? "Today" : f === "week" ? "This Week" : f === "month" ? "This Month" : "This Year"}
              </Button>
            ))}
            <Button variant="outline" size="sm">
              <Calendar className="w-4 h-4" />
              Custom
            </Button>
          </div>
        </div>

        {/* Orders Table */}
        <div className="bg-card rounded-2xl border shadow-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground">
                    Order ID
                  </th>
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground">
                    Customer
                  </th>
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground hidden md:table-cell">
                    Phone
                  </th>
                  <th className="text-left px-5 py-4 text-sm font-semibold text-foreground hidden lg:table-cell">
                    Items
                  </th>
                  <th className="text-right px-5 py-4 text-sm font-semibold text-foreground">
                    Total
                  </th>
                  <th className="text-center px-5 py-4 text-sm font-semibold text-foreground">
                    Status
                  </th>
                  <th className="text-right px-5 py-4 text-sm font-semibold text-foreground">
                    ETA
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="text-center py-10 text-muted-foreground">
                      Loading orders...
                    </td>
                  </tr>
                ) : filteredOrders.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-10 text-muted-foreground">
                      No orders found.
                    </td>
                  </tr>
                ) : (
                  filteredOrders.map((order) => (
                    <tr
                      key={order.id}
                      className="hover:bg-muted/30 transition-colors"
                    >
                      <td className="px-5 py-4">
                        <span className="font-mono text-sm text-foreground">
                          {order.id}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="font-medium text-foreground">
                          {order.customer_name}
                        </span>
                      </td>
                      <td className="px-5 py-4 hidden md:table-cell">
                        <span className="text-sm text-muted-foreground">
                          {order.phone}
                        </span>
                      </td>
                      <td className="px-5 py-4 hidden lg:table-cell">
                        <span className="text-sm text-muted-foreground truncate max-w-xs block">
                          {order.items}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-right">
                        <span className="font-semibold text-foreground">
                          ${order.total.toFixed(2)}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-center">
                        <span
                          className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${
                            order.status === "confirmed"
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
                      </td>
                      <td className="px-5 py-4 text-right">
                        <span className="text-sm text-muted-foreground">
                          {order.eta}
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

export default Orders;
