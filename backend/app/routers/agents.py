"""智能体工作台 API — LangGraph 标准版"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

from app.services.agent_service import AgentService
from app.utils.dependencies import get_current_user_dep, require_role

router = APIRouter(prefix="/agents", tags=["智能体工作台"])
logger = logging.getLogger(__name__)


class GenerateRequest(BaseModel):
    student_id: int
    course_id: int
    knowledge_point_ids: List[int]
    resource_type: str
    difficulty: str
    generation_goal: Optional[str] = None
    enable_review: bool = True


class SaveResourceRequest(BaseModel):
    result: dict
    title: str
    course_id: int
    user_id: int = 0


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
    service = AgentService()

    async def event_stream():
        try:
            for step_event in service.generate_stream(req):
                yield f"data: {__import__('json').dumps(step_event, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"[Stream] {e}")
            yield f"data: {__import__('json').dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

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
    return result


@router.post("/save-resource")
async def save_resource(
    req: SaveResourceRequest,
    user: dict = Depends(require_role("teacher", "admin")),
):
    """保存生成的学习资源"""
    service = AgentService()
    return service.save_resource(req, user_id=user.get("user_id"))
