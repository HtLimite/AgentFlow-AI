from app.core.encoding import repair_mojibake, repair_mojibake_text


def test_repair_utf8_decoded_as_gb18030_text() -> None:
    broken = "璇疯皟鐢ㄧ煡璇嗗簱宸ュ叿鍥炵瓟鎶ラ攢娴佺▼鏄粈涔堬紵"
    assert repair_mojibake_text(broken) == "请调用知识库工具回答报销流程是什么？"


def test_repair_nested_audit_payload() -> None:
    payload = {
        "input": {
            "query": "璇疯皟鐢ㄧ煡璇嗗簱宸ュ叿鍥炵瓟鎶ラ攢娴佺▼鏄粈涔堬紵",
            "top_k": 3,
        },
        "output": {"chunks": []},
    }
    assert repair_mojibake(payload)["input"]["query"] == "请调用知识库工具回答报销流程是什么？"


def test_keep_normal_text_unchanged() -> None:
    text = "请调用知识库工具回答报销流程是什么？"
    assert repair_mojibake_text(text) == text
