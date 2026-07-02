import { Card } from "@/components/ui/card";

const agents = ["企业制度问答 Agent", "售后数据分析 Agent", "API 查询 Agent"];

export default function AgentsPage() {
  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {agents.map((name) => (
        <Card key={name}>
          <div className="text-lg font-semibold">{name}</div>
          <p className="mt-3 text-sm text-slate-400">支持 System Prompt、模型绑定、知识库绑定、工具调用日志。</p>
          <div className="mt-5 rounded-xl bg-white/10 p-3 text-sm text-slate-300">工具：knowledge_search / sql_query / http_request</div>
        </Card>
      ))}
    </div>
  );
}
