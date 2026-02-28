import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from nexaflow_crm.database import Base, engine
from nexaflow_crm.routers import auth_router, contacts, projects, invoices, dashboard

STATIC_DIR = Path(__file__).parent / "static"
IS_PRODUCTION = os.getenv("ENV", "development") != "development"

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://crm.zuhdi.id").split(",")

limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

app = FastAPI(
    title="NexaFlow CRM",
    version="1.0.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(auth_router.router)
app.include_router(contacts.router)
app.include_router(projects.router)
app.include_router(invoices.router)
app.include_router(dashboard.router)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


def start():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "6001"))
    reload = os.getenv("ENV", "development") == "development"
    uvicorn.run("nexaflow_crm.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    start()
