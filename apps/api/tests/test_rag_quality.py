from app.services.chunk_service import chunk_service
from app.services.persistent_knowledge_service import _lexical_score
from app.services.rerank_service import rerank_service

DOC = """# 求职项目实践建议

# 0. 项目最终定位

项目名称：

```txt
AI DevOps Control Panel
AI 智能部署与项目运维平台
```

一句话介绍：

```txt
面向个人开发者和小团队的 AI 辅助 DevOps 控制台，支持 GitHub 仓库接入、Docker 服务监控、日志智能诊断、Docker Compose 配置生成、Nginx 反向代理配置生成和部署记录管理。
```

## 第 4 周：工程化、部署、简历包装

### Day 25：GitHub Actions

后端 CI:

```txt
mvn test
mvn package
docker build
```
"""


def test_markdown_chunk_keeps_heading_context() -> None:
    chunks = chunk_service.split_text(DOC, chunk_size=500, overlap=80)
    contents = [str(item["content"]) for item in chunks]
    assert any("项目最终定位" in content and "一句话介绍" in content for content in contents)
    assert not any(content.strip() in {"t", "us", "端 CI"} for content in contents)


def test_intro_question_scores_target_chunk_higher_than_ci_chunk() -> None:
    question = "AI DevOps Control Panel 这个项目的一句话介绍是什么?"
    target = "项目最终定位\n一句话介绍：面向个人开发者和小团队的 AI 辅助 DevOps 控制台，支持 GitHub 仓库接入、Docker 服务监控。"
    ci = "后端 CI: mvn test mvn package docker build 每次 push 自动构建 README 展示 build badge"
    assert _lexical_score(question, target) > _lexical_score(question, ci)


def test_rerank_prefers_project_intro_for_intro_question() -> None:
    question = "AI DevOps Control Panel 这个项目的一句话介绍是什么?"
    ranked = rerank_service.rerank(
        question,
        [
            {"content": "后端 CI: mvn test mvn package docker build", "score": 0.55, "vector_score": 0.1, "document": "doc.md", "chunk_index": 9},
            {"content": "项目最终定位\n一句话介绍：面向个人开发者和小团队的 AI 辅助 DevOps 控制台。", "score": 0.65, "vector_score": 0.1, "document": "doc.md", "chunk_index": 1},
        ],
        top_k=1,
    )
    assert "一句话介绍" in ranked[0]["content"]
