# 部署说明

## Docker Compose

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

## 服务

| 服务 | 端口 | 说明 |
|---|---:|---|
| web | 3000 | Next.js 管理台 |
| api | 8000 | FastAPI 后端 |
| postgres | 5432 | PostgreSQL + pgvector |
| redis | 6379 | 缓存与任务队列预留 |
| minio | 9000 / 9001 | 文件存储与控制台 |
| nginx | 8080 | 统一入口 |

## 生产化建议

- 将密钥放入服务器环境变量或密钥管理服务
- API 与 Web 分别构建镜像并打版本
- PostgreSQL 使用云数据库或独立持久卷
- MinIO 使用对象存储替代
- Nginx 配置 HTTPS
- GitHub Actions 增加 Docker 镜像构建与发布
