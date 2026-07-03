import { cn } from "@/components/ui/cn";

type BadgeVariant = "default" | "success" | "warning" | "danger" | "info";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantClassName: Record<BadgeVariant, string> = {
  default: "border-border bg-surface text-foreground",
  success: "border-success/30 bg-success-soft text-success-foreground",
  warning: "border-warning/30 bg-warning-soft text-warning-foreground",
  danger: "border-danger/30 bg-danger-soft text-danger-foreground",
  info: "border-info/30 bg-info-soft text-info-foreground",
};

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return <span className={cn("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium", variantClassName[variant], className)} {...props} />;
}
