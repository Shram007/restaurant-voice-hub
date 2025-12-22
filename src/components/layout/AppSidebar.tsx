import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  ShoppingBag,
  Phone,
  UtensilsCrossed,
  Settings,
  Zap,
  ChevronLeft,
  ChevronRight,
  Mic,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { title: "Overview", icon: LayoutDashboard, path: "/" },
  { title: "Orders", icon: ShoppingBag, path: "/orders" },
  { title: "Call Logs", icon: Phone, path: "/calls" },
  { title: "Menu & FAQs", icon: UtensilsCrossed, path: "/menu" },
  { title: "Setup", icon: Zap, path: "/setup" },
  { title: "Settings", icon: Settings, path: "/settings" },
];

export function AppSidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col",
        collapsed ? "w-[72px]" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-16 border-b border-sidebar-border">
        <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-primary text-primary-foreground">
          <Mic className="w-5 h-5" />
        </div>
        {!collapsed && (
          <div className="animate-fade-in">
            <h1 className="font-bold text-foreground">VoiceOrder</h1>
            <p className="text-xs text-muted-foreground">AI Assistant</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group",
                isActive
                  ? "bg-primary text-primary-foreground shadow-card"
                  : "text-sidebar-foreground hover:bg-sidebar-accent"
              )}
            >
              <item.icon
                className={cn(
                  "w-5 h-5 flex-shrink-0 transition-transform duration-200",
                  !isActive && "group-hover:scale-110"
                )}
              />
              {!collapsed && (
                <span className="font-medium animate-fade-in">{item.title}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="p-3 border-t border-sidebar-border">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-full h-10 rounded-xl text-muted-foreground hover:bg-sidebar-accent transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-5 h-5" />
          ) : (
            <ChevronLeft className="w-5 h-5" />
          )}
        </button>
      </div>
    </aside>
  );
}
