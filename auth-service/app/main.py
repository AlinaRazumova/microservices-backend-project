from fastapi import FastAPI

from .database import Base, engine
from .routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Auth Service",
    description="Authentication and user management service",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "Auth Service",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }