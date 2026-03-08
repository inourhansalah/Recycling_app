import os
import uuid

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.utils.dependencies import get_current_user
from app.config import (
    UPLOAD_DIR,
    MAX_FILE_SIZE_MB,
    ALLOWED_FILE_TYPES
)

router = APIRouter(prefix="/uploads", tags=["Uploads"])


# Note: Directory creation is handled in main.py


# =====================================================
# ✅ Upload File (JWT Required)
# =====================================================
@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    # Validate content type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="File type not allowed"
        )

    # Validate size
    contents = await file.read()

    max_size = MAX_FILE_SIZE_MB * 1024 * 1024
    if len(contents) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large (max {MAX_FILE_SIZE_MB}MB)"
        )

    # Generate unique filename
    ext = file.filename.split(".")[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"

    file_path = os.path.join(UPLOAD_DIR, unique_name)

    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)

    return {
        "filename": unique_name,
        "url": f"/uploads/{unique_name}",
        "content_type": file.content_type
    }


# =====================================================
# ✅ Serve Uploaded Files
# =====================================================
@router.get("/{filename}")
def get_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")

    return FileResponse(file_path)