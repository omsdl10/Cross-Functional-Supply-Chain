from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.retrieval.contracts import (
    build_contract_chunks,
    ingest_supplier_contracts,
    query_supplier_contracts,
)


def test_build_contract_chunks() -> None:
    chunks = build_contract_chunks()

    assert len(chunks) >= 3
    assert {chunk.supplier_id for chunk in chunks} >= {"SUP-102", "SUP-207"}
    assert all(chunk.text for chunk in chunks)


def test_ingest_and_query_supplier_contracts(tmp_path: Path) -> None:
    ingest_result = ingest_supplier_contracts(chroma_path=tmp_path)

    assert ingest_result["documents_indexed"] >= 3
    assert ingest_result["chunks_indexed"] >= 3

    results = query_supplier_contracts(
        "Which supplier can be activated when inventory cover drops below 5 days?",
        chroma_path=tmp_path,
    )

    assert results
    assert any(result["metadata"]["supplier_id"] == "SUP-207" for result in results)


def test_retrieval_api_query(tmp_path: Path, monkeypatch) -> None:
    from app.api import retrieval as retrieval_api

    monkeypatch.setattr(
        retrieval_api,
        "query_supplier_contracts",
        lambda query, n_results=3: [
            {
                "text": "Atlas Energy Materials may be activated when inventory cover drops below 5 days.",
                "metadata": {"supplier_id": "SUP-207"},
                "distance": 0.12,
            }
        ],
    )

    client = TestClient(app)
    response = client.get(
        "/retrieval/contracts/query",
        params={"q": "inventory cover below 5 days", "n_results": 1},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "inventory cover below 5 days"
    assert body["results"][0]["metadata"]["supplier_id"] == "SUP-207"
