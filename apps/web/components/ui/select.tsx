import { forwardRef } from "react";
import { cn } from "@/components/ui/cn";

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean;
}

interface SelectFieldProps extends React.HTMLAttributes<HTMLLabelElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select({ className, error, children, ...props }, ref) {
  return (
    <select
      ref={ref}
      className={cn(
        "w-full rounded-xl border bg-panel/60 px-4 py-3 text-sm text-foreground outline-none transition focus:ring-2 disabled:cursor-not-allowed disabled:opacity-60",
        error ? "border-danger/60 focus:border-danger/70 focus:ring-danger/20" : "border-border focus:border-primary/55 focus:ring-primary/20",
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
});

export function SelectOption({ className, ...props }: React.OptionHTMLAttributes<HTMLOptionElement>) {
  return <option className={cn("bg-panel text-foreground", className)} {...props} />;
}

export function SelectField({ className, label, hint, error, children, ...props }: SelectFieldProps) {
  return (
    <label className={cn("block text-sm text-muted-foreground", className)} {...props}>
      {label ? <span className="mb-1 block font-medium text-foreground">{label}</span> : null}
      {children}
      {error ? <span className="mt-1 block text-xs text-danger-foreground">{error}</span> : hint ? <span className="mt-1 block text-xs text-muted-foreground/75">{hint}</span> : null}
    </label>
  );
}
