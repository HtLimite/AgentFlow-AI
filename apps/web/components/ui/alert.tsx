import { cn } from "@/components/ui/cn";

type AlertVariant = "info" | "success" | "warning" | "error" | "muted";

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
  title?: string;
}

const variantClassName: Record<AlertVariant, string> = {
  info: "border-info/30 bg-info-soft text-info-foreground",
  success: "border-success/30 bg-success-soft text-success-foreground",
  warning: "border-warning/30 bg-warning-soft text-warning-foreground",
  error: "border-danger/30 bg-danger-soft text-danger-foreground",
  muted: "border-border bg-surface/50 text-muted-foreground",
};

export function Alert({ className, variant = "info", title, children, ...props }: AlertProps) {
  return (
    <div className={cn("rounded-2xl border p-4 text-sm leading-6", variantClassName[variant], className)} role={variant === "error" ? "alert" : "status"} {...props}>
      {title ? <div className="mb-1 font-semibold text-foreground">{title}</div> : null}
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
