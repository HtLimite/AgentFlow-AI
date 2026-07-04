from app.schemas.workflow import WorkflowDefinition
from app.services.workflow_engine import workflow_engine


def _def():
    return WorkflowDefinition(
        nodes=[
            {"id": "start", "type": "start", "data": {}},
            {"id": "cond", "type": "condition", "data": {"key": "value", "operator": "equals", "value": "go"}},
            {"id": "yes", "type": "end", "data": {"label": "yes-branch"}},
            {"id": "no", "type": "end", "data": {"label": "no-branch"}},
        ],
        edges=[
            {"source": "start", "target": "cond"},
            {"source": "cond", "target": "yes", "condition": "true"},
            {"source": "cond", "target": "no", "condition": "false"},
        ],
    )


def test_condition_branch_follows_true_edge() -> None:
    import asyncio

    result = asyncio.run(workflow_engine.run(workflow_id=1, input_data={"question": "x", "value": "go"}, definition=_def()))
    node_ids = [run["node_id"] for run in result["node_runs"]]
    assert "yes" in node_ids
    assert "no" not in node_ids


def test_condition_branch_follows_false_edge() -> None:
    import asyncio

    result = asyncio.run(workflow_engine.run(workflow_id=1, input_data={"question": "x", "value": "stop"}, definition=_def()))
    node_ids = [run["node_id"] for run in result["node_runs"]]
    assert "no" in node_ids
    assert "yes" not in node_ids


def test_condition_operators_gt_lt() -> None:
    import asyncio

    definition = WorkflowDefinition(
        nodes=[
            {"id": "start", "type": "start", "data": {}},
            {"id": "cond", "type": "condition", "data": {"key": "n", "operator": "gt", "value": 5}},
            {"id": "big", "type": "end", "data": {}},
            {"id": "small", "type": "end", "data": {}},
        ],
        edges=[
            {"source": "start", "target": "cond"},
            {"source": "cond", "target": "big", "condition": "true"},
            {"source": "cond", "target": "small", "condition": "false"},
        ],
    )
    result = asyncio.run(workflow_engine.run(workflow_id=1, input_data={"question": "x", "n": 10}, definition=definition))
    assert any(run["node_id"] == "big" for run in result["node_runs"])

    result = asyncio.run(workflow_engine.run(workflow_id=1, input_data={"question": "x", "n": 2}, definition=definition))
    assert any(run["node_id"] == "small" for run in result["node_runs"])
