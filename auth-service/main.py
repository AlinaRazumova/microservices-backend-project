from fastapi import FastAPI

app = FastAPI(
    title="Auth Service",
    description="Service responsible for authentication and user management",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Auth Service is running"}
