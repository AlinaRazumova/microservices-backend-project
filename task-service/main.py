from fastapi import FastAPI

app = FastAPI(
    title="Task Service",
    description="Service responsible for task management",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Task Service is running"}
