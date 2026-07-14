"""
多模态 API 路由：图片理解等
"""
import base64
import logging

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import BaseModel

from app.config import get_settings
from app.services.iflytek_multimodal import image_understand

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/multimodal", tags=["Multimodal"])


class ImageUnderstandResponse(BaseModel):
    success: bool
    content: str = ""
    error: str = ""


@router.post("/image/understand", response_model=ImageUnderstandResponse)
async def understand_image(
    file: UploadFile = File(...),
    question: str = Form(default="详细描述这张图片的内容"),
):
    """
    图片理解：上传图片 + 问题，返回 AI 分析结果。

    - **file**: 图片文件（jpg/png，最大 4MB）
    - **question**: 对图片的提问
    """
    settings = get_settings()

    try:
        contents = await file.read()
        image_b64 = base64.b64encode(contents).decode("utf-8")

        result = image_understand(
            image_base64=image_b64,
            question=question,
            app_id=settings.iflytek_app_id,
            api_key=settings.iflytek_api_key,
            api_secret=settings.iflytek_api_secret,
        )

        if result:
            return ImageUnderstandResponse(success=True, content=result)
        else:
            return ImageUnderstandResponse(success=False, error="图片分析失败，请稍后重试")

    except Exception as e:
        logger.error(f"[Multimodal] image understand failed: {e}")
        return ImageUnderstandResponse(success=False, error=str(e))
