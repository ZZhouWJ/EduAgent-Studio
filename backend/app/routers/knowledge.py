"""
课程知识库 API 路由。

提供资料上传、解析、检索、列表、详情等接口。
"""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile

from app.services.auth_service import get_current_user_dependency as get_current_user
from app.services import knowledge_service

router = APIRouter(prefix="/knowledge", tags=["课程知识库"])


@router.post("/materials")
async def upload_material(
    course_id: int = Form(..., description="课程 ID"),
    file: UploadFile = File(..., description="上传的文件"),
    token: str = Depends(get_current_user),
):
    """
    上传课程资料文件。

    支持 PDF、Markdown、Word、PPT、TXT 格式。
    上传后状态为 pending，需要调用 /parse 接口触发解析。
    """
    # 读取文件内容
    file_content = await file.read()

    # 获取文件类型
    filename = file.filename or "unknown"
    file_type = _get_file_type(filename)

    if file_type is None:
        return {
            "code": 400,
            "message": "不支持的文件类型，支持: pdf, markdown, word, ppt, txt",
            "data": None,
        }

    # 获取当前用户 ID（从 token 解析，简化处理）
    user_id = _get_user_id_from_token(token)

    service = knowledge_service.KnowledgeService()
    return service.upload_material(
        course_id=course_id,
        file_content=file_content,
        filename=filename,
        file_type=file_type,
        created_by=user_id,
    )


@router.get("/materials")
async def list_materials(
    course_id: int = Query(..., description="课程 ID"),
    token: str = Depends(get_current_user),
):
    """
    获取课程资料列表。

    返回该课程下所有已上传的资料及其解析状态。
    """
    service = knowledge_service.KnowledgeService()
    return service.get_materials(course_id)


@router.get("/materials/{material_id}")
async def get_material_detail(
    material_id: int = Path(..., gt=0, description="资料 ID"),
    token: str = Depends(get_current_user),
):
    """
    获取资料详情。

    返回资料元数据及所有 chunks。
    """
    service = knowledge_service.KnowledgeService()
    return service.get_material_detail(material_id)


@router.post("/materials/{material_id}/parse")
async def parse_material(
    material_id: int = Path(..., gt=0, description="资料 ID"),
    token: str = Depends(get_current_user),
):
    """
    解析课程资料。

    读取文件内容，切分 chunks，提取关键词，存入数据库。
    解析完成后状态变为 parsed。
    """
    service = knowledge_service.KnowledgeService()
    return service.parse_material(material_id)


@router.get("/search")
async def search_knowledge(
    course_id: int = Query(..., description="课程 ID"),
    query: str = Query(..., min_length=1, description="查询文本"),
    kp_id: Optional[int] = Query(None, description="限定知识点 ID"),
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    token: str = Depends(get_current_user),
):
    """
    检索课程知识库。

    使用 BM25 算法检索与查询文本最相关的 chunks。
    返回按相关度排序的文档片段。
    """
    service = knowledge_service.KnowledgeService()
    return service.search(
        course_id=course_id,
        query=query,
        kp_id=kp_id,
        limit=limit,
    )


@router.delete("/materials/{material_id}")
async def delete_material(
    material_id: int = Path(..., gt=0, description="资料 ID"),
    token: str = Depends(get_current_user),
):
    """
    删除课程资料（软删除）。

    会同时删除关联的 chunks。
    """
    service = knowledge_service.KnowledgeService()
    return service.delete_material(material_id)


def _get_file_type(filename: str) -> Optional[str]:
    """根据文件名后缀判断文件类型。"""
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        return "pdf"
    elif filename_lower.endswith((".md", ".markdown")):
        return "markdown"
    elif filename_lower.endswith((".doc", ".docx")):
        return "word"
    elif filename_lower.endswith((".ppt", ".pptx")):
        return "ppt"
    elif filename_lower.endswith((".txt", ".text")):
        return "txt"
    else:
        return None


def _get_user_id_from_token(token: str) -> int:
    """
    从 token 中提取用户 ID。
    """
    from app.services.auth_service import get_current_user
    user = get_current_user(token)
    if user is None:
        return 0
    return user.get("user_id", 0)
