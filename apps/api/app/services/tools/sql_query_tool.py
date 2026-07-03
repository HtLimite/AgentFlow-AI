from typing import Any


class SQLQueryTool:
    name = "sql_query"
    description = "只读 SQL 查询工具演示版。"
    args_schema = {"sql": "string"}

    _blocked = ("insert", "update", "delete", "drop", "truncate", "alter", "create")

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        sql = str(args.get("sql", "")).strip()
        lowered = sql.lower()
        if not lowered.startswith("select"):
            raise ValueError("Only SELECT statements are allowed")
        if any(keyword in lowered for keyword in self._blocked):
            raise ValueError("Unsafe SQL keyword detected")
        return {
            "sql": sql,
            "columns": ["date", "orders", "refunds"],
            "rows": [["2026-07-01", 128, 3], ["2026-07-02", 142, 4]],
            "note": "demo dataset",
        }
