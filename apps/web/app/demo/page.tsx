import type { Route } from "next";
import Link from "next/link";
import { Card } from "@/components/ui/card";

const steps = [
  { title: "1. Showcase", href: "/showcase", desc: "用 30 秒讲清楚项目定位与价值。" },
  { title: "2. Knowledge RAG", href: "/knowledge", desc: "上传文档，展示引用来源和检索证据。" },
  { title: "3. Agent Audit", href: "/audit", desc: "展示 trace_id、工具输入输出和耗时。" },
  { title: "4. Workflow Canvas", href: "/workflows", desc: "展示节点运行链路和节点详情。" },
  { title: "5. Eval Compare", href: "/evals", desc: "横向比较 Prompt/模型效果。" },
  { title: "6. Verification", href: "/verification", desc: "最后用系统体检收尾。" },
];

export default function DemoPage() {
  return (
    <div className="space-y-6">
      <Card>
        <div className="text-sm uppercase tracking-[0.3em] text-blue-200">Online Demo Script</div>
        <h1 className="mt-4 text-3xl font-bold">AgentFlow-AI V3 演示动线</h1>
        <p className="mt-4 max-w-3xl text-slate-300">
          这是一条适合面试、录屏和在线 Demo 的展示路线：从平台定位，到 RAG、Agent 审计、工作流画布、评测对比，最后用验收中心证明完整性。
        </p>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {steps.map((step) => (
          <Link key={step.href} href={step.href as Route}>
            <Card className="h-full transition hover:-translate-y-1 hover:border-blue-400/50">
              <h2 className="text-lg font-semibold">{step.title}</h2>
              <p className="mt-3 text-sm text-slate-400">{step.desc}</p>
            </Card>
          </Link>
        ))}
      </div>

      <Card>
        <h2 className="text-xl font-semibold">3 分钟讲解词</h2>
        <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
          <p>AgentFlow-AI 不是一个聊天页面，而是企业 AI 应用平台，覆盖模型接入、知识库 RAG、Agent 工具调用、工作流编排、Prompt 管理、调用日志、成本统计、效果评测和 Docker 部署。</p>
          <p>V3 的重点是平台感：工作流不只是 JSON 执行，而是有可视化画布；Agent 不只是返回答案，而是有工具审计；Prompt 不只是调参，而是可以用评测集对比效果。</p>
          <p>最后通过 Verification 页面证明核心链路可启动、可运行、可验收，适合作为 AI 应用工程化求职作品。</p>
        </div>
      </Card>
    </div>
  );
}
