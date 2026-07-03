from app.services.vector_service import vector_service


def test_vector_service_is_deterministic() -> None:
    left = vector_service.embed("报销流程是什么")
    right = vector_service.embed("报销流程是什么")
    assert left == right
    assert len(left) == 64


def test_vector_cosine_self_similarity() -> None:
    vector = vector_service.embed("知识库检索")
    assert vector_service.cosine(vector, vector) > 0.99
