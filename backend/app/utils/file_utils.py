import os
import uuid
from fastapi import UploadFile, HTTPException


class FileUtils:
    """
    Handles file validation, naming, and saving.
    Responsible only for file-level operations.
    """

    ALLOWED_EXTENSIONS = {".pdf", ".txt"}

    @staticmethod
    def validate_file(file: UploadFile) -> str:
        """
        Validate file extension and type.
        """
        try:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in FileUtils.ALLOWED_EXTENSIONS:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported file type: {ext}"
                )
            return ext
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File validation failed: {str(e)}")

    @staticmethod
    def generate_filename(original_name: str) -> str:
        """
        Generate a unique filename using UUID.
        """
        ext = os.path.splitext(original_name)[1]
        unique_id = uuid.uuid4().hex
        return f"{unique_id}{ext}"

    @staticmethod
    def save_file(file: UploadFile, upload_dir: str = "data/uploads") -> str:
        """
        Save uploaded file to disk in upload_dir.
        """
        try:
            os.makedirs(upload_dir, exist_ok=True)
            filename = FileUtils.generate_filename(file.filename)
            file_path = os.path.join(upload_dir, filename)

            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())

            return file_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")