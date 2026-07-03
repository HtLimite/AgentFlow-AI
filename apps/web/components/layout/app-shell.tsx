import Link from "next/link";
import { navigationItems } from "@/lib/navigation";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-72 shrink-0 border-r border-white/10 bg-slate-950/70 p-5 lg:block">
        <div className="mb-8">
          <div className="text-xl font-bold">AgentFlow-AI</div>
          <div className="mt-1 text-sm text-slate-400">企业级 AI Agent 平台</div>
        </div>
        <nav className="space-y-2">
          {navigationItems.map((item) => (
            <Link key={item.href} href={item.href} className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-slate-300 transition hover:bg-white/10 hover:text-white">
              <span className="w-5 text-center text-slate-400">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-5 lg:p-8">
        <header className="mb-6 flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.05] px-5 py-4 backdrop-blur">
          <div>
            <div className="text-sm text-slate-400">真实运行时 · RAG / Agent / Workflow / Eval</div>
            <h1 className="text-lg font-semibold">AI 工作流控制台</h1>
          </div>
          <div className="rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 py-1 text-xs text-emerald-200">Local Ready</div>
        </header>
        {children}
      </main>
    </div>
  );
}
