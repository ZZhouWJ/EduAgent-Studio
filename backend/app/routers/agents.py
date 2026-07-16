"""智能体工作台 API — LangGraph 标准版"""
import logging
from typing import Annotated, List, Literal, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, StringConstraints

from app.services.agent_service import AgentService, extract_resource_references
from app.services.course_access_service import CourseAccessService
from app.utils.dependencies import get_current_user_dep, require_role

router = APIRouter(prefix="/agents", tags=["智能体工作台"])
logger = logging.getLogger(__name__)

ResourceType = Literal[
    "lecture",
    "mindmap",
    "quiz",
    "case",
    "code_case",
    "ppt",
    "video_script",
    "experiment_report",
    "error_analysis",
    "learning_card",
    "review",
    "test",
    "other",
]


class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)
    knowledge_point_ids: List[Annotated[int, Field(gt=0)]] = Field(
        ..., min_length=1, max_length=50
    )
    resource_type: ResourceType
    difficulty: Literal["basic", "intermediate", "advanced"]
    generation_goal: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
    ] = None


class SaveResourceRequest(BaseModel):
    result: dict
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    course_id: int = Field(..., gt=0)


PptText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


class PptSlideRequest(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    points: List[PptText] = Field(
        default_factory=list,
        max_length=12,
        validation_alias=AliasChoices("points", "bullets"),
    )
    notes: Optional[Annotated[str, StringConstraints(max_length=2000)]] = None


class ExportPptxRequest(BaseModel):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    slides: List[PptSlideRequest] = Field(..., min_length=1, max_length=40)


@router.get("/list")
async def list_agents(user: dict = Depends(get_current_user_dep)):
    """获取智能体列表（登录用户均可访问）"""
    service = AgentService()
    return service.list_agents()


@router.post("/generate")
async def generate_learning_resource(
    req: GenerateRequest,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    执行多智能体协作，生成个性化学习资源。

    LangGraph 工作流由 Supervisor 自动编排：
    diagnosis → planning → generation → assessment → teacher_review
    → (若质量 < 7.0 → revision → teacher_review) 最多循环 3 次
    """
    CourseAccessService().require_generation_context(
        req.course_id, req.student_id, req.knowledge_point_ids, user
    )
    service = AgentService()
    result = service.generate(req)
    if result.get("code") != 0:
        raise HTTPException(status_code=500, detail=result.get("message"))
    return result


@router.post("/generate/stream")
async def generate_stream(
    req: GenerateRequest,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """
    流式执行多智能体工作流。

    使用 Server-Sent Events（SSE）逐节点推送中间结果。
    前端可实时渲染每个 Agent 的执行状态和产出。
    """
    CourseAccessService().require_generation_context(
        req.course_id, req.student_id, req.knowledge_point_ids, user
    )
    service = AgentService()

    async def event_stream():
        try:
            for step_event in service.generate_stream(req):
                yield f"data: {__import__('json').dumps(step_event, ensure_ascii=False)}\n\n"
        except Exception as exc:
            logger.error("智能体流式生成失败 (%s)", type(exc).__name__)
            yield f"data: {__import__('json').dumps({'type': 'error', 'message': '生成失败，请稍后重试'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/workflow/{run_id}")
async def get_workflow_status(
    run_id: str,
    user: dict = Depends(get_current_user_dep),
):
    """
    查询某个工作流运行的状态（从 Checkpoint 恢复）。

    用于断点续传场景，支持工作流暂停后从 SQLite Checkpoint 恢复。
    """
    service = AgentService()
    result = service.get_workflow_status(run_id)
    if result.get("code") == 404:
        raise HTTPException(status_code=404, detail=result.get("message"))
    raw = ((result.get("data") or {}).get("_raw") or {})
    course_id = raw.get("course_id")
    student_id = raw.get("student_id")
    if course_id is None or student_id is None:
        raise HTTPException(status_code=404, detail="工作流上下文不完整")
    CourseAccessService().require_workflow_access(
        int(course_id), int(student_id), user
    )
    return result


@router.post("/save-resource")
async def save_resource(
    req: SaveResourceRequest,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """保存生成的学习资源"""
    access = CourseAccessService()
    access.require_course_access(req.course_id, user)
    references = extract_resource_references(req.result)
    access.require_knowledge_points_course(req.course_id, references["kp_ids"])
    access.require_material_chunks_course(req.course_id, references["chunk_ids"])
    service = AgentService()
    return service.save_resource(req, user_id=user.get("user_id"))


@router.post("/export/pptx")
async def export_pptx(
    req: ExportPptxRequest,
    user: dict = Depends(get_current_user_dep),
):
    """将已生成的结构化课件导出为可编辑的 PPTX 文件。"""
    from app.services.ppt_export_service import build_presentation

    output = build_presentation(
        req.title,
        [slide.model_dump() for slide in req.slides],
    )
    safe_name = "".join(
        char for char in req.title if char not in '\\/:*?"<>|'
    ).strip() or "EduAgent课件"
    encoded_name = quote(f"{safe_name}.pptx")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}",
            "Cache-Control": "no-store",
        },
    )
