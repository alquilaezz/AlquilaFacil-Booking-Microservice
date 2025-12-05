from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import reservations, reports

app = FastAPI(title="Booking Service")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(reservations.router)
app.include_router(reports.router)
