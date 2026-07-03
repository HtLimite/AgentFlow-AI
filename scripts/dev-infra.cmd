@echo off
setlocal
echo Starting AgentFlow-AI infrastructure: postgres redis minio
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio

echo.
echo Waiting for PostgreSQL to be ready...
for /l %%i in (1,1,30) do (
  docker exec agentflow-postgres pg_isready -U agentflow -d agentflow >nul 2>nul
  if not errorlevel 1 goto postgres_ready
  timeout /t 2 /nobreak >nul
)

echo PostgreSQL did not become ready in time.
exit /b 1

:postgres_ready
echo PostgreSQL is ready.
echo Applying local database migrations from deploy/postgres/*.sql ...
docker exec agentflow-postgres sh -lc "for f in /docker-entrypoint-initdb.d/*.sql; do echo Applying $f; psql -v ON_ERROR_STOP=1 -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -f \"$f\"; done"
if errorlevel 1 (
  echo Database migration failed.
  exit /b 1
)

echo.
echo Infrastructure started and migrations applied.
echo PostgreSQL: localhost:5432
echo Redis: localhost:6379
echo MinIO API: localhost:9000
echo MinIO Console: localhost:9001
endlocal
