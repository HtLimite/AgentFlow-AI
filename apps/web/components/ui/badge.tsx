import { cn } from "@/components/ui/cn";

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return <span className={cn("inline-flex rounded-full border border-white/10 bg-white/10 px-2.5 py-1 text-xs text-slate-200", className)} {...props} />;
}
