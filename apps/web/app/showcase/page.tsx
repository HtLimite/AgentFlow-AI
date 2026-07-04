import type { Route } from "next";
import Link from "next/link";
import { Card } from "@/components/ui/card";

const modules = [
  { title: "模型供应商", desc: "固定选项输入、连接测试、敏感信息脱敏。", href: "/settings" },
  { title: "知识库 RAG", desc: "文档上传、文本清洗、切片检索、引用来源。", href: "/knowledge" },
  { title: "Agent 工具调用", desc: "Tool Registry、tool_calls、工具输入输出可追踪。", href: "/agents" },
  { title: "工作流编排", desc: "节点协议、执行器、node_runs 链路展示。", href: "/workflows" },
  { title: "Prompt 管理", desc: "模板、变量渲染、版本管理演示。", href: "/prompts" },
  { title: "效果评测", desc: "评测集、逐题评分、原因说明。", href: "/evals" },
];

export default function ShowcasePage() {
  return (
    <div className="space-y-6">
      <Card className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 via-transparent to-emerald-500/10" />
        <div className="relative">
          <div className="text-sm uppercase tracking-[0.3em] text-primary">AgentFlow-AI Showcase</div>
          <h1 className="mt-4 text-3xl font-bold md:text-5xl">企业级 AI Agent 工作流与知识库平台</h1>
          <p className="mt-5 max-w-3xl text-muted-foreground">
            覆盖模型接入、RAG、Agent 工具调用、Workflow、Prompt、日志成本、Eval 和 Docker 部署，适合作为 AI 应用工程化求职项目展示。
          </p>
          <div className="mt-6 flex flex-wrap gap-3 text-sm">
            <Link href="/verification" className="rounded-full bg-white px-5 py-2 font-medium text-background">运行验收中心</Link>
            <Link href="/dashboard" className="rounded-full border border-border px-5 py-2 text-foreground">进入控制台</Link>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {modules.map((item) => (
            <Link key={item.href} href={item.href as Route}>
            <Card className="h-full transition hover:-translate-y-1 hover:border-primary/50">
              <h2 className="text-lg font-semibold">{item.title}</h2>
              <p className="mt-3 text-sm text-muted-foreground">{item.desc}</p>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <h2 className="text-xl font-semibold">面试讲解重点</h2>
        <div className="mt-4 grid gap-3 text-sm text-muted-foreground md:grid-cols-2">
          <div className="rounded-xl bg-surface/60 p-4">不是单纯聊天 Demo，而是企业 AI 应用闭环。</div>
          <div className="rounded-xl bg-surface/60 p-4">RAG 回答带引用来源，降低幻觉风险。</div>
          <div className="rounded-xl bg-surface/60 p-4">Agent 工具调用链路可观察、可排查。</div>
          <div className="rounded-xl bg-surface/60 p-4">Prompt、Eval、成本统计体现工程化思维。</div>
        </div>
      </Card>
    </div>
  );
}
