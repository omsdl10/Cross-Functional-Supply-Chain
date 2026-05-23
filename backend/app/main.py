from fastapi import FastAPI

from app.api.retrieval import router as retrieval_router
from app.api.tools import router as tools_router

APP_NAME = "cross-functional-supply-chain-concierge"
APP_STAGE = "stage-4-operational-tools"

app = FastAPI(
    title="Cross-Functional Supply Chain Concierge",
    description="Autonomous supplier risk and inventory orchestration system.",
    version="0.1.0",
)

app.include_router(retrieval_router)
app.include_router(tools_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": APP_NAME,
        "stage": APP_STAGE,
    }
