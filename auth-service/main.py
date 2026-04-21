from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Auth Service is running"}
