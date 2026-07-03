import { cn } from "@/components/ui/cn";
import { uiTheme } from "@/components/ui/theme";

type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg" | "icon";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const variantClassName: Record<ButtonVariant, string> = {
  primary: "bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary/85",
  secondary: "border border-border bg-surface text-foreground hover:bg-surface-strong",
  outline: "border border-border bg-transparent text-foreground hover:border-primary/45 hover:bg-primary-soft",
  ghost: "bg-transparent text-muted-foreground hover:bg-surface hover:text-foreground",
  danger: "bg-danger text-danger-foreground shadow-lg shadow-danger/20 hover:bg-danger/85",
};

const sizeClassName: Record<ButtonSize, string> = {
  sm: "h-9 px-3 text-xs",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-5 text-base",
  icon: "h-10 w-10 p-0",
};

export function Button({ className, variant = "primary", size = "md", type = "button", ...props }: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition disabled:cursor-not-allowed disabled:opacity-60",
        uiTheme.focusRing,
        variantClassName[variant],
        sizeClassName[size],
        className
      )}
      {...props}
    />
  );
}
