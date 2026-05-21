from fastapi import FastAPI

APP_NAME = "cross-functional-supply-chain-concierge"
APP_STAGE = "stage-1-foundation"

app = FastAPI(
    title="Cross-Functional Supply Chain Concierge",
    description="Autonomous supplier risk and inventory orchestration system.",
    version="0.1.0",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": APP_NAME,
        "stage": APP_STAGE,
    }
