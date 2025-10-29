from fastapi import FastAPI
from backend.app.routes import file_upload, qa_routes
from backend.app.utils.database import engine, Base

app = FastAPI(title="Document Processing API")

Base.metadata.create_all(bind=engine)

app.include_router(file_upload.router)
app.include_router(qa_routes.router)


@app.get("/")
def home():
    return {"message": "Welcome to the Document Processing API 🚀"}
