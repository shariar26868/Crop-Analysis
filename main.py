from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS, SENTRY_DSN
from app.exceptions import register_exception_handlers
from app.routers import farms, crops, markets, auth as auth_router, admin as admin_router
from app.logging_setup import init_logging

try:
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
except Exception:
    sentry_sdk = None
    SentryAsgiMiddleware = None

app = FastAPI(
    title="Agriculture DB API",
    description="Farm Performance & Crop Market Intelligence API for agriculture_db",
    version="1.0.0",
)


init_logging()
if SENTRY_DSN and sentry_sdk is not None:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.1)

register_exception_handlers(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farms.router)
app.include_router(crops.router)
app.include_router(markets.router)
app.include_router(auth_router.router)
app.include_router(admin_router.router)

if SENTRY_DSN and SentryAsgiMiddleware is not None:
    app.add_middleware(SentryAsgiMiddleware)


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "running",
        "docs": "/docs",
        "endpoints": [
            "GET /farms/summary",
            "GET /farms/{farm_id}/performance",
            "GET /farms/top",
            "GET /farms/loss-analysis",
            "GET /crops/yield-efficiency",
            "GET /crops/seasonal-trend",
            "GET /markets/price-comparison",
            "GET /crops/quality-breakdown",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",  port=8000, reload=True)