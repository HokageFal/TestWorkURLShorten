import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from src.database import Database
from src.services.shortener import URLShortenerService
from src.routers import links

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortening service",
    version="0.1.0"
)

db = Database()
service = URLShortenerService(db)

app.include_router(links.router, tags=["links"])


@app.get("/")
async def root():
    return {"status": "ok", "service": "url-shortener"}
