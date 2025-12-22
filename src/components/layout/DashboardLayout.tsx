import { ReactNode, useState, useEffect } from "react";
import { AppSidebar } from "./AppSidebar";
import { cn } from "@/lib/utils";

interface DashboardLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export function DashboardLayout({ children, title, subtitle }: DashboardLayoutProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Listen to sidebar state changes
  useEffect(() => {
    const checkSidebar = () => {
      const sidebar = document.querySelector('aside');
      if (sidebar) {
        setSidebarCollapsed(sidebar.classList.contains('w-[72px]'));
      }
    };
    
    const observer = new MutationObserver(checkSidebar);
    const sidebar = document.querySelector('aside');
    if (sidebar) {
      observer.observe(sidebar, { attributes: true, attributeFilter: ['class'] });
    }
    
    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <AppSidebar />
      <main
        className={cn(
          "transition-all duration-300",
          sidebarCollapsed ? "ml-[72px]" : "ml-64"
        )}
      >
        {/* Header */}
        <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-sm border-b border-border">
          <div className="px-6 lg:px-8 py-4">
            <h1 className="text-2xl font-bold text-foreground">{title}</h1>
            {subtitle && (
              <p className="text-sm text-muted-foreground mt-0.5">{subtitle}</p>
            )}
          </div>
        </header>

        {/* Content */}
        <div className="p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
