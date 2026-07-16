"""对象存储 API — 学习资源文件下载"""
import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.services.storage_service import get_resource_content
from app.services.course_access_service import CourseAccessService
from app.utils.dependencies import get_current_user_dep

router = APIRouter(prefix="/storage", tags=["对象存储"])


@router.get("/{file_id}")
async def download_resource(
    file_id: UUID,
    user: dict = Depends(get_current_user_dep),
):
    """
    根据 file_id 下载学习资源 JSON 文件。

    文件从 backend/data/storage/ 目录读取（按 course_id/YYYY-MM/ 组织）。
    """
    entry = get_resource_content(str(file_id))
    if not entry:
        raise HTTPException(status_code=404, detail="文件不存在")

    course_id = entry.get("course_id")
    if course_id is None:
        raise HTTPException(status_code=404, detail="文件不存在")
    CourseAccessService().require_course_access(int(course_id), user)

    file_path = entry.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    title = str(entry.get("title") or "resource")
    safe_title = "".join(
        char for char in title if char not in "\r\n/\\"
    ).strip()[:120] or "resource"
    return FileResponse(
        file_path,
        media_type="application/json; charset=utf-8",
        filename=f"{safe_title}.json",
    )
