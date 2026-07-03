import { forwardRef } from "react";
import { cn } from "@/components/ui/cn";

interface FieldProps extends React.HTMLAttributes<HTMLLabelElement> {
  label?: string;
  hint?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(function Input({ className, ...props }, ref) {
  return (
    <input
      ref={ref}
      className={cn(
        "w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-blue-300/50 focus:ring-2 focus:ring-blue-300/20 disabled:cursor-not-allowed disabled:opacity-60",
        className
      )}
      {...props}
    />
  );
});

export const Textarea = forwardRef<HTMLTextAreaElement, React.TextareaHTMLAttributes<HTMLTextAreaElement>>(function Textarea({ className, ...props }, ref) {
  return (
    <textarea
      ref={ref}
      className={cn(
        "min-h-28 w-full rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-blue-300/50 focus:ring-2 focus:ring-blue-300/20 disabled:cursor-not-allowed disabled:opacity-60",
        className
      )}
      {...props}
    />
  );
});

export function Field({ className, label, hint, error, children, ...props }: FieldProps) {
  return (
    <label className={cn("block text-sm text-slate-300", className)} {...props}>
      {label ? <span className="mb-1 block font-medium text-slate-200">{label}</span> : null}
      {children}
      {error ? <span className="mt-1 block text-xs text-red-300">{error}</span> : hint ? <span className="mt-1 block text-xs text-slate-500">{hint}</span> : null}
    </label>
  );
}
