from fastapi import FastAPI

from app.api.approval import router as approval_router
from app.api.demo import router as demo_router
from app.api.execution import router as execution_router
from app.api.impact import router as impact_router
from app.api.monitor import router as monitor_router
from app.api.retrieval import router as retrieval_router
from app.api.strategy import router as strategy_router
from app.api.tools import router as tools_router

APP_NAME = "cross-functional-supply-chain-concierge"
APP_STAGE = "stage-10-end-to-end-demo"

app = FastAPI(
    title="Cross-Functional Supply Chain Concierge",
    description="Autonomous supplier risk and inventory orchestration system.",
    version="0.1.0",
)

app.include_router(retrieval_router)
app.include_router(tools_router)
app.include_router(monitor_router)
app.include_router(impact_router)
app.include_router(strategy_router)
app.include_router(approval_router)
app.include_router(execution_router)
app.include_router(demo_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": APP_NAME,
        "stage": APP_STAGE,
    }
