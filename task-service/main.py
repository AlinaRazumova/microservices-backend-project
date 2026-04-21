from fastapi import FastAPI

app = FastAPI(title="Task Service")

@app.get("/")
def root():
    return {"message": "Task Service is running"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "task-service"}
