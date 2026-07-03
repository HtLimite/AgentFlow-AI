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
        "w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm text-foreground outline-none transition disabled:cursor-not-allowed disabled:opacity-60",
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
        "min-h-28 w-full rounded-xl border border-border bg-panel/60 px-4 py-3 text-sm text-foreground outline-none transition disabled:cursor-not-allowed disabled:opacity-60",
        className
      )}
      {...props}
    />
  );
});

export function Field({ className, label, hint, error, children, ...props }: FieldProps) {
  return (
    <label className={cn("block text-sm text-muted-foreground", className)} {...props}>
      {label ? <span className="mb-1 block font-medium text-foreground">{label}</span> : null}
      {children}
      {error ? <span className="mt-1 block text-xs text-danger-foreground">{error}</span> : hint ? <span className="mt-1 block text-xs text-muted-foreground/75">{hint}</span> : null}
    </label>
  );
}
