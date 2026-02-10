from fastapi import FastAPI

app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortening service",
    version="0.1.0"
)


@app.get("/")
async def root():
    return {"status": "ok", "service": "url-shortener"}
