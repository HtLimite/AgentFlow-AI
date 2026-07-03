@echo off
setlocal
echo Starting AgentFlow-AI infrastructure: postgres redis minio
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
echo.
echo Infrastructure started.
echo PostgreSQL: localhost:5432
echo Redis: localhost:6379
echo MinIO API: localhost:9000
echo MinIO Console: localhost:9001
endlocal
