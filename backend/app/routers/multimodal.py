"""
多模态 API 路由：图片理解等
"""
import base64
import asyncio
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.config import get_settings
from app.services.iflytek_multimodal import image_understand
from app.utils.dependencies import get_current_user_dep

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multimodal", tags=["Multimodal"])
MAX_IMAGE_BYTES = 4 * 1024 * 1024
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/png"}


class ImageUnderstandResponse(BaseModel):
    success: bool
    content: str = ""
    error: str = ""


@router.post("/image/understand", response_model=ImageUnderstandResponse)
async def understand_image(
    file: UploadFile = File(...),
    question: str = Form(default="详细描述这张图片的内容"),
    user: dict = Depends(get_current_user_dep),
):
    """
    图片理解：上传图片 + 问题，返回 AI 分析结果。

    - **file**: 图片文件（jpg/png，最大 4MB）
    - **question**: 对图片的提问
    """
    settings = get_settings()

    try:
        if file.content_type not in SUPPORTED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail="仅支持 JPG、JPEG 和 PNG 图片")
        contents = await file.read(MAX_IMAGE_BYTES + 1)
        if not contents:
            raise HTTPException(status_code=400, detail="图片文件不能为空")
        if len(contents) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="图片不能超过 4MB")
        clean_question = question.strip()
        if not clean_question or len(clean_question) > 2000:
            raise HTTPException(status_code=400, detail="问题长度应为 1 到 2000 个字符")
        if not all((settings.iflytek_app_id, settings.iflytek_api_key, settings.iflytek_api_secret)):
            raise HTTPException(status_code=503, detail="图片理解服务尚未配置")

        image_b64 = base64.b64encode(contents).decode("utf-8")

        result = await asyncio.to_thread(
            image_understand,
            image_base64=image_b64,
            question=clean_question,
            app_id=settings.iflytek_app_id,
            api_key=settings.iflytek_api_key,
            api_secret=settings.iflytek_api_secret,
        )

        if result:
            return ImageUnderstandResponse(success=True, content=result)
        else:
            return ImageUnderstandResponse(success=False, error="图片分析失败，请稍后重试")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Multimodal] image understand failed: {e}")
        return ImageUnderstandResponse(success=False, error="图片分析失败，请稍后重试")
