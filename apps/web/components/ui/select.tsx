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
        "w-full rounded-xl border bg-slate-950/60 px-4 py-3 text-sm text-slate-100 outline-none transition focus:ring-2 disabled:cursor-not-allowed disabled:opacity-60",
        error ? "border-red-400/50 focus:border-red-300/70 focus:ring-red-300/20" : "border-white/10 focus:border-blue-300/50 focus:ring-blue-300/20",
        className
      )}
      {...props}
    >
      {children}
    </select>
  );
});

export function SelectOption({ className, ...props }: React.OptionHTMLAttributes<HTMLOptionElement>) {
  return <option className={cn("bg-slate-950 text-slate-100", className)} {...props} />;
}

export function SelectField({ className, label, hint, error, children, ...props }: SelectFieldProps) {
  return (
    <label className={cn("block text-sm text-slate-300", className)} {...props}>
      {label ? <span className="mb-1 block font-medium text-slate-200">{label}</span> : null}
      {children}
      {error ? <span className="mt-1 block text-xs text-red-300">{error}</span> : hint ? <span className="mt-1 block text-xs text-slate-500">{hint}</span> : null}
    </label>
  );
}
