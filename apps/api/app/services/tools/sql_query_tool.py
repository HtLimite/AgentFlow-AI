from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text

from app.core.database import engine


class SQLQueryTool:
    name = "sql_query"
    description = "只读 SQL 查询工具，连接当前 AgentFlow 数据库执行 SELECT / WITH 查询。"
    args_schema = {"sql": "string", "max_rows": "integer"}

    _blocked = ("insert", "update", "delete", "drop", "truncate", "alter", "create", "grant", "revoke", "copy")

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        sql = str(args.get("sql", "")).strip()
        max_rows = min(max(int(args.get("max_rows") or 100), 1), 500)
        self._validate_readonly_sql(sql)

        async with engine.connect() as conn:
            result = await conn.execute(text(sql))
            columns = list(result.keys())
            rows = [
                [self._to_json_value(value) for value in row]
                for row in result.fetchmany(max_rows)
            ]

        return {
            "sql": sql,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": len(rows) >= max_rows,
            "source": "database",
        }

    def _validate_readonly_sql(self, sql: str) -> None:
        if not sql:
            raise ValueError("SQL 不能为空")
        normalized = sql.rstrip(";").strip()
        if ";" in normalized:
            raise ValueError("Only one SQL statement is allowed")
        lowered = normalized.lower()
        if not (lowered.startswith("select") or lowered.startswith("with")):
            raise ValueError("Only SELECT / WITH readonly statements are allowed")
        if any(keyword in lowered for keyword in self._blocked):
            raise ValueError("Unsafe SQL keyword detected")

    def _to_json_value(self, value: Any) -> Any:
        if isinstance(value, datetime | date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value
