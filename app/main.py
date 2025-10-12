from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.routes import router
from app.core.logging_config import setup_logging
from app.core.config import settings

setup_logging()

app = FastAPI(title="Phi Neutralizer Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {
        "service": "Phi Neutralizer",
        "status": "running",
        "phi_model_url": settings.phi_model_url
    }