from app.services.tool_audit_service import ToolAuditService


def test_tool_audit_records_and_summarizes_calls() -> None:
    service = ToolAuditService()
    item = service.record(
        trace_id="trace-test",
        agent_id=1,
        tool_name="calculator",
        input_data={"expression": "1+1"},
        output_data={"result": 2},
        status="success",
        latency_ms=12,
    )

    assert item["id"] == 1
    assert item["trace_id"] == "trace-test"
    assert service.get_record(1) is not None
    summary = service.summary()
    assert summary["total_calls"] == 1
    assert summary["success_rate"] == 1
    assert summary["tool_counts"]["calculator"] == 1
