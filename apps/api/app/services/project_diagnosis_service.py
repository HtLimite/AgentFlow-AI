import re
from typing import Any


class ProjectDiagnosisService:
    """Rule-based project diagnosis used as the first useful DevOps workflow."""

    _patterns = [
        {
            "id": "port_conflict",
            "category": "runtime",
            "title": "端口冲突或端口绑定失败",
            "severity": "critical",
            "regex": re.compile(r"address already in use|port is already allocated|listen eaddrinuse|bind.*failed|端口.*占用", re.IGNORECASE),
            "cause": "宿主机或其他容器已经占用了目标端口，常见于 Nginx 80/443 或 API 8000/8080。",
        },
        {
            "id": "database_connection",
            "category": "database",
            "title": "数据库连接失败",
            "severity": "critical",
            "regex": re.compile(r"connection refused|could not connect|database.*(failed|error)|psycopg|sqlalchemy|ECONNREFUSED|数据库.*失败", re.IGNORECASE),
            "cause": "数据库容器未启动、连接地址写成了错误主机名，或本地 uv 模式和 Docker service name 混用。",
        },
        {
            "id": "missing_env",
            "category": "configuration",
            "title": "环境变量缺失或未复制 .env",
            "severity": "warning",
            "regex": re.compile(r"env.*not found|missing.*env|undefined.*environment|找不到.*\.env|环境变量.*缺失", re.IGNORECASE),
            "cause": "项目没有加载 .env，或关键变量未配置。",
        },
        {
            "id": "nginx_upstream",
            "category": "network",
            "title": "Nginx 反向代理上游不可达",
            "severity": "critical",
            "regex": re.compile(r"502 bad gateway|upstream.*failed|connect\(\).*failed|no live upstreams|nginx.*502", re.IGNORECASE),
            "cause": "Nginx 指向的端口没有服务监听，或容器端口没有映射到宿主机。",
        },
        {
            "id": "node_dependency",
            "category": "frontend",
            "title": "前端依赖或模块解析失败",
            "severity": "warning",
            "regex": re.compile(r"module not found|cannot find module|failed to compile|pnpm.*ERR|npm ERR|找不到模块", re.IGNORECASE),
            "cause": "依赖未安装、路径别名配置不一致，或 Node / pnpm 版本不匹配。",
        },
        {
            "id": "docker_unhealthy",
            "category": "docker",
            "title": "Docker 容器未健康运行",
            "severity": "warning",
            "regex": re.compile(r"unhealthy|exited \(1\)|restarting|container.*failed|healthcheck.*failed|容器.*重启", re.IGNORECASE),
            "cause": "容器启动命令、健康检查、数据库依赖或环境变量存在问题。",
        },
        {
            "id": "permission",
            "category": "filesystem",
            "title": "文件权限或路径访问异常",
            "severity": "warning",
            "regex": re.compile(r"permission denied|eacces|eperm|access is denied|权限不足|拒绝访问", re.IGNORECASE),
            "cause": "当前用户没有读写目录权限，或 Windows / Docker 挂载路径权限不一致。",
        },
    ]

    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        project_name = str(payload.get("project_name") or "未命名项目")
        runtime = str(payload.get("runtime") or "未说明")
        repository_url = payload.get("repository_url")
        question = str(payload.get("question") or "")
        logs = str(payload.get("logs") or "")
        files = payload.get("files") if isinstance(payload.get("files"), list) else []
        services = payload.get("services") if isinstance(payload.get("services"), list) else []

        corpus = self._build_corpus(question, logs, files, services)
        signals = self._detect_signals(corpus, files, services)
        if not corpus.strip():
            signals.append(
                {
                    "id": "insufficient_input",
                    "category": "input",
                    "title": "输入信息不足",
                    "severity": "warning",
                    "detail": "当前没有提供日志、关键配置文件或服务状态，诊断只能给出通用检查路径。",
                    "evidence": "logs/files/services 为空",
                }
            )

        likely_causes = self._build_causes(signals)
        actions = self._build_actions(signals)
        score = self._readiness_score(signals)
        severity = self._overall_severity(signals)
        summary = self._summary(project_name, runtime, score, severity, signals)

        return {
            "project_name": project_name,
            "repository_url": repository_url,
            "runtime": runtime,
            "summary": summary,
            "readiness_score": score,
            "severity": severity,
            "signals": signals,
            "likely_causes": likely_causes,
            "actions": actions,
            "artifacts": self._build_artifacts(project_name, summary, signals, actions),
            "next_verification": self._verification_steps(signals),
            "mode": "local_rules_devops_diagnosis",
        }

    def demo_payload(self) -> dict[str, Any]:
        return {
            "project_name": "AgentFlow-AI",
            "repository_url": "git@github.com:HtLimite/AgentFlow-AI.git",
            "runtime": "Windows 本地 uv + Docker PostgreSQL / Redis / MinIO",
            "question": "本地启动后页面能打开，但接口和 Docker 服务不稳定，帮我判断下一步。",
            "logs": "Bind for 0.0.0.0:80 failed: port is already allocated\npsycopg.OperationalError: connection refused\ncontainer agentflow-api exited (1)",
            "files": [
                {
                    "path": "deploy/docker-compose.yml",
                    "content": "services:\n  postgres:\n    image: pgvector/pgvector:pg16\n  redis:\n    image: redis:7-alpine\n",
                }
            ],
            "services": [
                {"name": "agentflow-postgres", "status": "running", "detail": "healthy"},
                {"name": "agentflow-api", "status": "exited", "detail": "connection refused"},
            ],
        }

    def _build_corpus(self, question: str, logs: str, files: list[Any], services: list[Any]) -> str:
        file_text = "\n".join(f"{item.get('path', '')}\n{item.get('content', '')}" for item in files if isinstance(item, dict))
        service_text = "\n".join(f"{item.get('name', '')} {item.get('status', '')} {item.get('detail', '')}" for item in services if isinstance(item, dict))
        return "\n".join([question, logs, file_text, service_text])

    def _detect_signals(self, corpus: str, files: list[Any], services: list[Any]) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        for item in self._patterns:
            match = item["regex"].search(corpus)
            if not match:
                continue
            signals.append(
                {
                    "id": item["id"],
                    "category": item["category"],
                    "title": item["title"],
                    "severity": item["severity"],
                    "detail": item["cause"],
                    "evidence": self._evidence(corpus, match.group(0)),
                }
            )

        paths = [str(item.get("path", "")).lower() for item in files if isinstance(item, dict)]
        if any("docker-compose" in path for path in paths):
            signals.append(
                {
                    "id": "compose_present",
                    "category": "docker",
                    "title": "已提供 Docker Compose 配置",
                    "severity": "info",
                    "detail": "可以基于 compose 文件继续检查服务名、端口映射、健康检查和依赖关系。",
                    "evidence": ", ".join(path for path in paths if "docker-compose" in path),
                }
            )
        if services:
            unhealthy = [item for item in services if isinstance(item, dict) and str(item.get("status", "")).lower() not in {"running", "healthy", "up", "ok"}]
            if unhealthy:
                signals.append(
                    {
                        "id": "service_status_unhealthy",
                        "category": "runtime",
                        "title": "服务状态存在异常",
                        "severity": "warning",
                        "detail": "至少一个服务不是 running / healthy / up 状态，需要优先查看该服务日志。",
                        "evidence": "; ".join(f"{item.get('name')}={item.get('status')}" for item in unhealthy),
                    }
                )
        return signals

    def _evidence(self, corpus: str, needle: str) -> str:
        index = corpus.lower().find(needle.lower())
        if index < 0:
            return needle[:160]
        start = max(index - 80, 0)
        end = min(index + len(needle) + 120, len(corpus))
        return corpus[start:end].replace("\n", " ").strip()[:260]

    def _build_causes(self, signals: list[dict[str, Any]]) -> list[str]:
        mapping = {
            "port_conflict": "端口被已有服务占用，导致 Docker 或 Nginx 无法绑定。",
            "database_connection": "本地 uv 与 Docker 网络环境混用，DATABASE_URL 主机名需要区分 localhost 和 service name。",
            "missing_env": "未复制 .env 或关键密钥、数据库、Redis、MinIO 变量缺失。",
            "nginx_upstream": "反向代理 upstream 指向了未监听端口或未暴露的容器端口。",
            "node_dependency": "前端依赖、Node 版本或路径别名不一致。",
            "docker_unhealthy": "容器启动后依赖未就绪或健康检查失败。",
            "permission": "本地目录、Docker volume 或脚本执行权限不足。",
        }
        result = [mapping[item["id"]] for item in signals if item.get("id") in mapping]
        if not result:
            result.append("当前没有明显错误模式，建议补充启动日志、docker ps、关键配置文件后再诊断。")
        return result

    def _build_actions(self, signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ids = {str(item.get("id")) for item in signals}
        actions: list[dict[str, Any]] = []
        if "port_conflict" in ids:
            actions.append(
                {
                    "title": "先定位端口占用，再决定改端口或停服务",
                    "reason": "端口冲突会让服务根本无法启动，优先级最高。",
                    "steps": [
                        "Windows 执行 netstat -ano | findstr :80 或 :8000，确认占用进程。",
                        "如果是宝塔 / 本机 Nginx 占用 80，Docker Nginx 改用 8081:80 或只保留宝塔反代。",
                        "修改 compose ports 后重新 docker compose up -d。",
                    ],
                    "command": "netstat -ano | findstr :80",
                    "risk": "low",
                }
            )
        if "database_connection" in ids:
            actions.append(
                {
                    "title": "修正本地 uv 与 Docker 模式的数据库地址",
                    "reason": "本地 uv 访问 Docker PostgreSQL 应使用 localhost，容器内 API 才使用 postgres service name。",
                    "steps": [
                        "本地 uv 模式设置 DATABASE_URL=postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow。",
                        "完整 Docker 模式设置 DATABASE_URL=postgresql+psycopg://agentflow:agentflow@postgres:5432/agentflow。",
                        "重启后端并访问 /api/system/persistence/health。",
                    ],
                    "command": "curl http://localhost:8000/api/system/persistence/health",
                    "risk": "medium",
                }
            )
        if "nginx_upstream" in ids:
            actions.append(
                {
                    "title": "验证反代 upstream 是否真实可访问",
                    "reason": "502 通常不是前端问题，而是 Nginx 到后端 upstream 不通。",
                    "steps": [
                        "在宿主机执行 curl http://127.0.0.1:8000/health 或目标端口。",
                        "确认 docker compose ports 是否把 API 暴露到宿主机。",
                        "宝塔 Nginx 反代时优先指向 127.0.0.1:8000，而不是容器内部 service name。",
                    ],
                    "command": "curl http://127.0.0.1:8000/health",
                    "risk": "low",
                }
            )
        if "node_dependency" in ids:
            actions.append(
                {
                    "title": "重建前端依赖并跑生产构建",
                    "reason": "模块解析失败需要用构建命令验证，而不是只看 dev server。",
                    "steps": [
                        "确认 Node 版本满足项目要求。",
                        "执行 pnpm install。",
                        "执行 pnpm --filter @agentflow/web build 定位 TypeScript 或 import 错误。",
                    ],
                    "command": "pnpm --filter @agentflow/web build",
                    "risk": "low",
                }
            )
        if not actions:
            actions.append(
                {
                    "title": "补齐最小诊断输入并执行 4 个基础检查",
                    "reason": "当前没有足够错误证据，需要先建立可重复验收路径。",
                    "steps": [
                        "粘贴后端启动日志和浏览器报错。",
                        "补充 docker ps 输出和 .env 关键变量名。",
                        "执行 health、persistence health、verify-local、前端 build。",
                    ],
                    "command": "scripts\\verify-local.cmd",
                    "risk": "low",
                }
            )
        return actions

    def _readiness_score(self, signals: list[dict[str, Any]]) -> int:
        critical = sum(1 for item in signals if item.get("severity") == "critical")
        warning = sum(1 for item in signals if item.get("severity") == "warning")
        return max(20, min(100, 100 - critical * 22 - warning * 8))

    def _overall_severity(self, signals: list[dict[str, Any]]) -> str:
        severities = {item.get("severity") for item in signals}
        if "critical" in severities:
            return "critical"
        if "warning" in severities:
            return "warning"
        return "ok"

    def _summary(self, project_name: str, runtime: str, score: int, severity: str, signals: list[dict[str, Any]]) -> str:
        if severity == "critical":
            return f"{project_name} 当前不建议继续叠加功能，先处理启动/连接类阻塞问题；运行环境：{runtime}；可用度评分 {score}/100。"
        if severity == "warning":
            return f"{project_name} 已具备基础演示条件，但仍有配置或服务健康风险；运行环境：{runtime}；可用度评分 {score}/100。"
        if signals:
            return f"{project_name} 未发现明显阻塞错误，可以进入页面验收和真实数据接入；运行环境：{runtime}；可用度评分 {score}/100。"
        return f"{project_name} 缺少诊断输入，当前只能给出通用验收路径；运行环境：{runtime}；可用度评分 {score}/100。"

    def _build_artifacts(self, project_name: str, summary: str, signals: list[dict[str, Any]], actions: list[dict[str, Any]]) -> list[dict[str, str]]:
        report = [f"# {project_name} 项目诊断报告", "", "## 结论", summary, "", "## 发现"]
        for item in signals:
            report.append(f"- [{item.get('severity')}] {item.get('title')}：{item.get('detail')}")
        report.extend(["", "## 建议动作"])
        for item in actions:
            report.append(f"- {item.get('title')}：{item.get('reason')}")
        artifacts = [
            {
                "name": "diagnosis-report.md",
                "language": "markdown",
                "content": "\n".join(report),
            }
        ]
        ids = {str(item.get("id")) for item in signals}
        if ids & {"port_conflict", "nginx_upstream", "database_connection"}:
            artifacts.append(
                {
                    "name": "local-runtime-checklist.md",
                    "language": "markdown",
                    "content": "\n".join(
                        [
                            "# 本地运行检查清单",
                            "",
                            "- Docker 基础设施：scripts\\dev-infra.cmd",
                            "- uv 后端：scripts\\dev-api-uv.cmd",
                            "- 前端：pnpm dev:web",
                            "- 持久化健康：curl http://localhost:8000/api/system/persistence/health",
                            "- 全量验收：scripts\\verify-local.cmd",
                        ]
                    ),
                }
            )
        return artifacts

    def _verification_steps(self, signals: list[dict[str, Any]]) -> list[str]:
        steps = [
            "curl http://localhost:8000/health",
            "curl http://localhost:8000/api/system/persistence/health",
            "scripts\\verify-local.cmd",
            "pnpm --filter @agentflow/web build",
        ]
        if any(item.get("id") == "port_conflict" for item in signals):
            steps.insert(0, "netstat -ano | findstr :80")
        return steps


project_diagnosis_service = ProjectDiagnosisService()
