import { cn } from "@/components/ui/cn";

type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "danger";
type ButtonSize = "sm" | "md" | "lg" | "icon";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const variantClassName: Record<ButtonVariant, string> = {
  primary: "bg-blue-500 text-white shadow-lg shadow-blue-950/25 hover:bg-blue-400",
  secondary: "border border-white/10 bg-white/10 text-slate-100 hover:bg-white/15",
  outline: "border border-white/10 bg-transparent text-slate-100 hover:border-blue-300/40 hover:bg-blue-500/10",
  ghost: "bg-transparent text-slate-300 hover:bg-white/10 hover:text-white",
  danger: "bg-red-500 text-white shadow-lg shadow-red-950/20 hover:bg-red-400",
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
        "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition focus:outline-none focus:ring-2 focus:ring-blue-300/50 disabled:cursor-not-allowed disabled:opacity-60",
        variantClassName[variant],
        sizeClassName[size],
        className
      )}
      {...props}
    />
  );
}
