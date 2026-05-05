from fastapi import FastAPI

from .database import Base, engine
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Service",
    description="Task management service",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "Task Service",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }