import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function ChatPage() {
  return (
    <div className="grid gap-4 xl:grid-cols-[280px_1fr_320px]">
      <Card>
        <h2 className="font-semibold">会话列表</h2>
        <div className="mt-4 space-y-2 text-sm text-slate-300">
          <div className="rounded-xl bg-white/10 p-3">多模型对话测试</div>
          <div className="rounded-xl p-3 hover:bg-white/10">RAG 引用验证</div>
        </div>
      </Card>
      <Card className="min-h-[620px]">
        <h2 className="font-semibold">Chat Playground</h2>
        <div className="mt-5 space-y-4">
          <div className="rounded-2xl bg-blue-500/15 p-4 text-sm">用户：请总结这份知识库里的报销流程。</div>
          <div className="rounded-2xl bg-white/10 p-4 text-sm text-slate-200">AI：我会先检索知识库，再根据引用片段生成可核验答案。</div>
        </div>
        <div className="mt-8 flex gap-3">
          <input className="flex-1 rounded-xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm outline-none" placeholder="输入问题，后续接入 SSE 流式输出" />
          <Button>发送</Button>
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">模型参数</h2>
        <div className="mt-4 space-y-4 text-sm text-slate-300">
          <div>Model：DeepSeek / Qwen / OpenAI Compatible</div>
          <div>Temperature：0.7</div>
          <div>Max Tokens：2048</div>
          <div>Stream：开启</div>
        </div>
      </Card>
    </div>
  );
}
