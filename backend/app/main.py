from fastapi import FastAPI
from backend.app.routes import file_upload

app = FastAPI(title="Document Processing API")

app.include_router(file_upload.router)


@app.get("/")
def home():
    return {"message": "Welcome to the Document Processing API 🚀"}
