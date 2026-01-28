import { cn } from "@/lib/utils";

interface StatusIndicatorProps {
  status: "online" | "offline" | "busy";
  label: string;
  size?: "sm" | "md" | "lg";
}

const statusStyles = {
  online: {
    dot: "bg-success",
    text: "text-success",
    bg: "bg-success/10",
  },
  offline: {
    dot: "bg-muted-foreground",
    text: "text-muted-foreground",
    bg: "bg-muted",
  },
  busy: {
    dot: "bg-warning",
    text: "text-warning",
    bg: "bg-warning/10",
  },
};

const sizeStyles = {
  sm: {
    container: "px-2 py-1 text-xs gap-1.5",
    dot: "w-1.5 h-1.5",
  },
  md: {
    container: "px-3 py-1.5 text-sm gap-2",
    dot: "w-2 h-2",
  },
  lg: {
    container: "px-4 py-2 text-base gap-2.5",
    dot: "w-2.5 h-2.5",
  },
};

export function StatusIndicator({
  status,
  label,
  size = "md",
}: StatusIndicatorProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full font-medium",
        statusStyles[status].bg,
        statusStyles[status].text,
        sizeStyles[size].container
      )}
    >
      <span
        className={cn(
          "rounded-full animate-pulse",
          statusStyles[status].dot,
          sizeStyles[size].dot
        )}
      />
      {label}
    </div>
  );
}
