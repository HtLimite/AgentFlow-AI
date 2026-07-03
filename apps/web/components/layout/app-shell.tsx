"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/components/ui/cn";
import { navigationItems } from "@/lib/navigation";

function isActivePath(pathname: string, href: string) {
  if (href === "/") return pathname === href;
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-transparent">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-border bg-panel/85 p-5 shadow-2xl shadow-background/30 backdrop-blur-xl lg:flex lg:flex-col">
        <Link href="/dashboard" className="rounded-2xl border border-border bg-surface/40 p-4 transition hover:border-primary/40 hover:bg-primary-soft">
          <div className="text-xl font-bold tracking-tight text-foreground">AgentFlow-AI</div>
          <div className="mt-1 text-sm text-muted-foreground">企业级 AI Agent 平台</div>
        </Link>

        <nav className="mt-6 flex-1 space-y-1 overflow-y-auto pr-1">
          {navigationItems.map((item) => {
            const active = isActivePath(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition",
                  active
                    ? "border border-primary/30 bg-primary/15 text-foreground shadow-lg shadow-primary/10"
                    : "text-muted-foreground hover:bg-surface hover:text-foreground"
                )}
              >
                <span className={cn("flex h-8 w-8 items-center justify-center rounded-lg border text-xs font-semibold", active ? "border-primary/40 bg-primary/20 text-primary-foreground" : "border-border bg-surface/60 text-muted-foreground group-hover:text-foreground")}>{item.icon}</span>
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-5 rounded-2xl border border-success/20 bg-success-soft p-4 text-sm text-success-foreground">
          <div className="flex items-center justify-between gap-3">
            <span className="font-medium">Local Runtime</span>
            <Badge variant="success">Ready</Badge>
          </div>
          <p className="mt-2 text-xs leading-5 text-success-foreground/70">固定侧栏，内容区域独立滚动，适合控制台长页面使用。</p>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 border-b border-border bg-panel/75 backdrop-blur-xl">
          <div className="mx-auto max-w-[1600px] px-4 py-4 sm:px-5 lg:px-8">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Runtime Console</div>
                <h1 className="mt-1 text-lg font-semibold text-foreground">AI 工作流控制台</h1>
              </div>
              <div className="hidden items-center gap-2 rounded-full border border-success/30 bg-success-soft px-3 py-1 text-xs text-success-foreground sm:flex">
                <span className="h-2 w-2 rounded-full bg-success" />
                Local Ready
              </div>
            </div>

            <nav className="mt-4 flex gap-2 overflow-x-auto pb-1 lg:hidden">
              {navigationItems.map((item) => {
                const active = isActivePath(pathname, item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "shrink-0 rounded-full border px-3 py-2 text-xs transition",
                      active ? "border-primary/40 bg-primary/20 text-foreground" : "border-border bg-surface/50 text-muted-foreground hover:bg-surface hover:text-foreground"
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>
        </header>

        <main className="mx-auto max-w-[1600px] px-4 py-5 sm:px-5 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
  );
}
