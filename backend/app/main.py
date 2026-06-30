from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analyze, url_check, screenshot
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="TrustGuard AI",
    description="AI-powered Fake News & Scam Detector API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(url_check.router, prefix="/api/v1", tags=["URL Check"])
app.include_router(screenshot.router, prefix="/api/v1", tags=["Screenshot"])


@app.get("/")
def root():
    return {"message": "TrustGuard AI is running", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
