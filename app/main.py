from fastapi import FastAPI

from app.database.database import Base, engine
from app.models import models

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Robokidz Quiz Generator API",
    description="AI-powered lesson quiz generator",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Robokidz Quiz Generator API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }