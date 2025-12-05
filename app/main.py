from fastapi import FastAPI
from .database import Base, engine
from .routers import reservations, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking Service")

app.include_router(reservations.router)
app.include_router(reports.router)
