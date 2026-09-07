from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import metrics

app = FastAPI(
    title="GitHub Engineering Data Platform API",
    description="Exposes Gold-layer engineering metrics derived from GitHub activity.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://172.18.0.6:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(metrics.router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}