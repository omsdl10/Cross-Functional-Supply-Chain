from fastapi import APIRouter, Query

from app.retrieval.contracts import ingest_supplier_contracts, query_supplier_contracts


router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.post("/contracts/ingest")
def ingest_contracts() -> dict[str, int | str]:
    return ingest_supplier_contracts()


@router.get("/contracts/query")
def query_contracts(
    q: str = Query(..., min_length=3),
    n_results: int = Query(3, ge=1, le=10),
) -> dict[str, object]:
    return {
        "query": q,
        "results": query_supplier_contracts(q, n_results=n_results),
    }
