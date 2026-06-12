"""对象存储 API — 学习资源文件下载"""
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.services.storage_service import get_resource_content
from app.services.auth_service import get_current_user_dependency as get_current_user

router = APIRouter(prefix="/storage", tags=["对象存储"])


@router.get("/{file_id}")
async def download_resource(
    file_id: str,
    token: str = Depends(get_current_user),
):
    """
    根据 file_id 下载学习资源 JSON 文件。

    文件从 backend/data/storage/ 目录读取（按 course_id/YYYY-MM/ 组织）。
    """
    entry = get_resource_content(file_id)
    if not entry:
        raise HTTPException(status_code=404, detail="文件不存在")

    file_path = entry.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        file_path,
        media_type="application/json; charset=utf-8",
        filename=f"{entry.get('title', 'resource')}.json",
    )
