import { cn } from "@/components/ui/cn";

type BadgeVariant = "default" | "success" | "warning" | "danger" | "info";

interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantClassName: Record<BadgeVariant, string> = {
  default: "border-white/10 bg-white/10 text-slate-200",
  success: "border-emerald-400/30 bg-emerald-400/10 text-emerald-100",
  warning: "border-amber-400/30 bg-amber-400/10 text-amber-100",
  danger: "border-red-400/30 bg-red-400/10 text-red-100",
  info: "border-blue-400/30 bg-blue-400/10 text-blue-100",
};

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return <span className={cn("inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium", variantClassName[variant], className)} {...props} />;
}
