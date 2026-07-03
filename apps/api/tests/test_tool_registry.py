import asyncio

from app.services.tool_service import tool_registry


def test_tool_registry_lists_core_tools() -> None:
    names = {item["name"] for item in tool_registry.list_tools()}
    assert {"knowledge_search", "calculator", "sql_query", "http_request"}.issubset(names)


def test_calculator_tool_runs() -> None:
    record = asyncio.run(tool_registry.run("calculator", {"expression": "1+2*3"}))
    assert record.status == "success"
    assert record.output["result"] == 7
