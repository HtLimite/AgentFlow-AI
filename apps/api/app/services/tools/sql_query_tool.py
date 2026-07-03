from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text

from app.core.database import engine

FORBIDDEN_SQL_TERMS = {
    " insert ",
    " update ",
    " delete ",
    " drop ",
    " alter ",
    " create ",
    " truncate ",
    " grant ",
    " revoke ",
    " copy ",
    " vacuum ",
    " analyze ",
}


class SQLQueryTool:
    name = "sql_query"
    description = "只读 SQL 查询工具，连接当前 AgentFlow 数据库执行安全 SELECT 查询。"
    args_schema = {"sql": "string", "max_rows": "integer"}

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        sql = str(args.get("sql", "")).strip()
        max_rows = min(max(int(args.get("max_rows") or 100), 1), 200)
        self._validate_readonly_sql(sql)

        async with engine.connect() as conn:
            result = await conn.execute(text(sql))
            columns = list(result.keys())
            rows = [[self._to_json_value(value) for value in row] for row in result.fetchmany(max_rows)]

        return {
            "sql": sql,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": len(rows) >= max_rows,
            "source": "database_safe_readonly",
        }

    def _validate_readonly_sql(self, sql: str) -> None:
        if not sql:
            raise ValueError("SQL cannot be empty")
        normalized = f" {sql.rstrip(';').strip().lower()} "
        if ";" in normalized:
            raise ValueError("Only one SQL statement is allowed")
        if not normalized.lstrip().startswith("select"):
            raise ValueError("Only SELECT statements are allowed")
        if any(term in normalized for term in FORBIDDEN_SQL_TERMS):
            raise ValueError("SQL contains a blocked keyword")
        if " pg_sleep" in normalized or " information_schema" in normalized:
            raise ValueError("System catalog and delay functions are blocked")

    def _to_json_value(self, value: Any) -> Any:
        if isinstance(value, datetime | date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value
