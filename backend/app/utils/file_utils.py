import os
import uuid
from fastapi import UploadFile, HTTPException


class FileUtils:
    """Handles file validation, naming, and saving."""

    ALLOWED_EXTENSIONS = {".pdf", ".txt"}

    @staticmethod
    def validate_file(file: UploadFile) -> str:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in FileUtils.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
        return ext

    @staticmethod
    def generate_filename(original_name: str) -> str:
        ext = os.path.splitext(original_name)[1]
        unique_id = uuid.uuid4().hex
        return f"{unique_id}{ext}"

    @staticmethod
    def save_file(file: UploadFile, upload_dir: str = "data/uploads") -> str:
        os.makedirs(upload_dir, exist_ok=True)
        filename = FileUtils.generate_filename(file.filename)
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        return file_path