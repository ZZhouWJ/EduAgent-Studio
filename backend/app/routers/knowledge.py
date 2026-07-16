"""
课程知识库 API 路由。

提供资料上传、解析、检索、列表、详情等接口。
"""

import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile
from pydantic import BaseModel

from app.services import knowledge_service
from app.services.course_access_service import CourseAccessService
from app.utils.dependencies import get_current_user_dep, require_role
from app.utils.exceptions import ForbiddenException

router = APIRouter(prefix="/knowledge", tags=["课程知识库"])
logger = logging.getLogger(__name__)


class KpLinkVerifyRequest(BaseModel):
    status: Literal["confirmed", "rejected"]


class ResourceEvidenceVerifyRequest(BaseModel):
    status: Literal["verified", "rejected"]


@router.post("/materials")
async def upload_material(
    course_id: int = Form(..., description="课程 ID"),
    file: UploadFile = File(..., description="上传的文件"),
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    上传课程资料文件。

    支持 PDF、Markdown、DOCX、PPTX、TXT 格式。
    上传后状态为 pending，需要调用 /parse 接口触发解析。
    """
    CourseAccessService().require_course_access(course_id, user)

    # Bounded read prevents direct API clients from forcing an unbounded allocation.
    file_content = await file.read(knowledge_service.MAX_MATERIAL_SIZE + 1)

    # 获取文件类型
    filename = file.filename or "unknown"
    file_type = _get_file_type(filename)

    if file_type is None:
        return {
            "code": 400,
            "message": "不支持的文件类型，支持: PDF、Markdown、DOCX、PPTX、TXT",
            "data": None,
        }

    service = knowledge_service.KnowledgeService()
    return service.upload_material(
        course_id=course_id,
        file_content=file_content,
        filename=filename,
        file_type=file_type,
        created_by=int(user["user_id"]),
    )


@router.get("/materials")
async def list_materials(
    course_id: int = Query(..., description="课程 ID"),
    user: dict = Depends(get_current_user_dep),
):
    """
    获取课程资料列表。

    返回该课程下所有已上传的资料及其解析状态。
    """
    CourseAccessService().require_course_access(course_id, user)
    service = knowledge_service.KnowledgeService()
    return service.get_materials(course_id)


@router.get("/materials/{material_id}")
async def get_material_detail(
    material_id: int = Path(..., gt=0, description="资料 ID"),
    user: dict = Depends(get_current_user_dep),
):
    """
    获取资料详情。

    返回资料元数据及所有 chunks。
    """
    CourseAccessService().require_material_access(material_id, user)
    service = knowledge_service.KnowledgeService()
    return service.get_material_detail(material_id)


@router.post("/materials/{material_id}/parse")
async def parse_material(
    material_id: int = Path(..., gt=0, description="资料 ID"),
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    解析课程资料。

    读取文件内容，切分 chunks，提取关键词，存入数据库。
    解析完成后状态变为 parsed。
    """
    CourseAccessService().require_material_access(material_id, user)
    service = knowledge_service.KnowledgeService()
    return service.parse_material(material_id)


@router.get("/search")
async def search_knowledge(
    course_id: int = Query(..., description="课程 ID"),
    query: str = Query(..., min_length=1, max_length=2000, description="查询文本"),
    kp_id: Optional[int] = Query(None, description="限定知识点 ID"),
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    user: dict = Depends(get_current_user_dep),
):
    """
    检索课程知识库。

    使用 BM25 算法检索与查询文本最相关的 chunks。
    返回按相关度排序的文档片段。
    """
    CourseAccessService().require_course_access(course_id, user)
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
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    删除课程资料（软删除）。

    会同时删除关联的 chunks。
    """
    CourseAccessService().require_material_access(material_id, user)
    service = knowledge_service.KnowledgeService()
    return service.delete_material(material_id)


# ================================================================
# 证据链路 API
# ================================================================

@router.get("/kp-chunk-links/pending")
async def get_pending_kp_chunk_links(
    course_id: Optional[int] = Query(None, description="课程 ID"),
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    获取待审核的知识点-Chunk 匹配列表。

    返回所有 status=pending 的匹配记录，供教师确认或拒绝。
    """
    if course_id is None and "admin" not in user.get("roles", []):
        raise ForbiddenException("教师查询待审核关联时必须指定本人课程")
    if course_id is not None:
        CourseAccessService().require_course_access(course_id, user)
    try:
        from app.repositories.evidence_repo import EvidenceRepository
        repo = EvidenceRepository()
        links = repo.get_pending_kp_chunk_links(course_id=course_id, limit=50)
        return {"code": 0, "message": "success", "data": links}
    except Exception as exc:
        logger.error("查询待审核知识点关联失败: course_id=%s (%s)", course_id, type(exc).__name__)
        return {"code": 500, "message": "查询失败，请稍后重试", "data": None}


@router.put("/kp-chunk-links/{link_id}/verify")
async def verify_kp_chunk_link(
    link_id: int = Path(..., gt=0, description="关联记录 ID"),
    payload: KpLinkVerifyRequest = ...,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    确认或拒绝一条知识点-Chunk 匹配。

    status = 'confirmed'：该匹配通过，可用于资源生成
    status = 'rejected'：该匹配不通过，忽略
    """
    CourseAccessService().require_kp_link_access(link_id, user)
    status = payload.status
    try:
        from app.repositories.evidence_repo import EvidenceRepository
        repo = EvidenceRepository()
        success = repo.verify_kp_chunk_link(link_id, status, int(user["user_id"]))
        if success:
            return {"code": 0, "message": f"已{'确认' if status == 'confirmed' else '拒绝'}", "data": {"link_id": link_id}}
        return {"code": 404, "message": "记录不存在", "data": None}
    except Exception as exc:
        logger.error("审核知识点关联失败: link_id=%s (%s)", link_id, type(exc).__name__)
        return {"code": 500, "message": "审核失败，请稍后重试", "data": None}


@router.get("/resource-evidence")
async def get_resource_evidence(
    resource_id: int = Query(..., gt=0, description="资源 ID"),
    user: dict = Depends(get_current_user_dep),
):
    """
    获取某资源的所有证据关联。

    返回资源生成时引用的所有教材原文片段及其审核状态。
    """
    CourseAccessService().require_resource_access(resource_id, user)
    try:
        from app.repositories.evidence_repo import EvidenceRepository
        repo = EvidenceRepository()
        evidence = repo.get_evidence_by_resource(resource_id)
        return {"code": 0, "message": "success", "data": evidence}
    except Exception as exc:
        logger.error("查询资源证据失败: resource_id=%s (%s)", resource_id, type(exc).__name__)
        return {"code": 500, "message": "查询失败，请稍后重试", "data": None}


@router.put("/resource-evidence/{link_id}/verify")
async def verify_resource_evidence(
    link_id: int = Path(..., gt=0, description="证据关联 ID"),
    payload: ResourceEvidenceVerifyRequest = ...,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    确认或拒绝一条资源证据。

    教师审核时使用：确认后证据链完整，可发布给学生。
    """
    CourseAccessService().require_evidence_link_access(link_id, user)
    status = payload.status
    try:
        from app.repositories.evidence_repo import EvidenceRepository
        repo = EvidenceRepository()
        success = repo.verify_resource_evidence_link(link_id, status, int(user["user_id"]))
        if success:
            return {"code": 0, "message": f"已{'确认' if status == 'verified' else '拒绝'}", "data": {"link_id": link_id}}
        return {"code": 404, "message": "记录不存在", "data": None}
    except Exception as exc:
        logger.error("审核资源证据失败: link_id=%s (%s)", link_id, type(exc).__name__)
        return {"code": 500, "message": "审核失败，请稍后重试", "data": None}


def _get_file_type(filename: str) -> Optional[str]:
    """根据文件名后缀判断文件类型。"""
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf"):
        return "pdf"
    elif filename_lower.endswith((".md", ".markdown")):
        return "markdown"
    elif filename_lower.endswith(".docx"):
        return "word"
    elif filename_lower.endswith(".pptx"):
        return "ppt"
    elif filename_lower.endswith((".txt", ".text")):
        return "txt"
    else:
        return None
