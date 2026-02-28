import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from nexaflow_crm.database import Base, engine
from nexaflow_crm.routers import auth_router, contacts, projects, invoices, dashboard

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="NexaFlow CRM", version="1.0.0")


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
    uvicorn.run("nexaflow_crm.main:app", host="0.0.0.0", port=6001, reload=True)


if __name__ == "__main__":
    start()
