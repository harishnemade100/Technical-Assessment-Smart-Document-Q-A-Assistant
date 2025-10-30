from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import file_upload, qa_routes, list_documents_route, delete_document_route
from backend.app.utils.database import engine, Base

app = FastAPI(title="Document Processing API")

Base.metadata.create_all(bind=engine)


# ✅ Register routers under one consistent prefix
app.include_router(file_upload.router, prefix="/api/documents")
app.include_router(list_documents_route.router, prefix="/api/documents")
app.include_router(delete_document_route.router, prefix="/api/documents")
app.include_router(qa_routes.router, prefix="/api/qa")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def home():
    return {"message": "Welcome to the Document Processing API 🚀"}
