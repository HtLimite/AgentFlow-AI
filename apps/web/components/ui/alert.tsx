import { cn } from "@/components/ui/cn";

type AlertVariant = "info" | "success" | "warning" | "error" | "muted";

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
  title?: string;
}

const variantClassName: Record<AlertVariant, string> = {
  info: "border-blue-400/30 bg-blue-400/10 text-blue-100",
  success: "border-emerald-400/30 bg-emerald-400/10 text-emerald-100",
  warning: "border-amber-400/30 bg-amber-400/10 text-amber-100",
  error: "border-red-400/30 bg-red-400/10 text-red-100",
  muted: "border-white/10 bg-white/5 text-slate-300",
};

export function Alert({ className, variant = "info", title, children, ...props }: AlertProps) {
  return (
    <div className={cn("rounded-2xl border p-4 text-sm leading-6", variantClassName[variant], className)} role={variant === "error" ? "alert" : "status"} {...props}>
      {title ? <div className="mb-1 font-semibold text-white">{title}</div> : null}
      {children}
    </div>
  );
}

export function ErrorAlert({ message, title = "操作失败", className }: { message?: string; title?: string; className?: string }) {
  if (!message) return null;
  return (
    <Alert variant="error" title={title} className={className}>
      {message}
    </Alert>
  );
}

export function StatusAlert({ message, title = "状态", variant = "muted", className }: { message?: string; title?: string; variant?: AlertVariant; className?: string }) {
  if (!message) return null;
  return (
    <Alert variant={variant} title={title} className={className}>
      {message}
    </Alert>
  );
}
