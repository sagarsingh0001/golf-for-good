"""File upload routes — winner proof screenshots."""
import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Response

from auth import get_current_user
from services.storage import put_object, get_object, build_path
from services import db as sdb

router = APIRouter(tags=["uploads"])

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/winners/{winner_id}/proof")
async def upload_proof(
    winner_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    winner = await sdb.select_one("winners", {"id": winner_id, "user_id": user["id"]})
    if not winner:
        raise HTTPException(404, "Winner entry not found")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(400, "File too large (max 5MB)")
    ct = file.content_type or "application/octet-stream"
    if ct not in ALLOWED_MIME:
        raise HTTPException(400, "Only image uploads are allowed")

    app_name = os.environ.get("APP_NAME", "golfforgood")
    path = build_path(app_name, user["id"], file.filename or "upload.bin")
    try:
        result = put_object(path, data, ct)
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {e}")

    await sdb.insert_one("files", {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "storage_path": result["path"],
        "original_filename": file.filename,
        "content_type": ct,
        "size": result.get("size", len(data)),
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    await sdb.update_by(
        "winners", {"id": winner_id},
        {
            "proof_storage_path": result["path"],
            "proof_uploaded_at": datetime.now(timezone.utc).isoformat(),
            "verification_status": "pending",
        },
    )

    return {"path": result["path"]}


@router.get("/files/view")
async def view_file(path: str, user: dict = Depends(get_current_user)):
    record = await sdb.select_one("files", {"storage_path": path, "is_deleted": False})
    if not record:
        raise HTTPException(404, "File not found")
    if record["user_id"] != user["id"] and user.get("role") != "admin":
        raise HTTPException(403, "Forbidden")
    try:
        data, _ = get_object(path)
    except Exception as e:
        raise HTTPException(500, f"Read failed: {e}")
    return Response(content=data, media_type=record.get("content_type", "application/octet-stream"))
