import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routes import router

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification Service",
    description="Notification service for task events",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"service": "Notification Service", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "notification-service"}
