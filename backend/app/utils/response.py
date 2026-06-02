"""
统一响应格式模块。

所有接口返回统一为：
{
    "code": 0,
    "message": "success",
    "data": {}
}

错误时：
{
    "code": 5000,
    "message": "错误信息",
    "data": null
}
"""

from typing import Any, Optional, Union

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 0,
) -> JSONResponse:
    """
    返回成功响应。

    Args:
        data: 响应数据体，默认为 None（转为 JSON null）
        message: 成功消息，默认为 "success"
        code: 业务状态码，默认为 0

    Returns:
        FastAPI JSONResponse
    """
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder({
            "code": code,
            "message": message,
            "data": data,
        }),
    )


def error_response(
    message: str,
    code: int = 5000,
    data: Any = None,
    status_code: int = 200,
) -> JSONResponse:
    """
    返回错误响应。

    Args:
        message: 错误描述（禁止包含密码、API Key 等敏感信息）
        code: 错误码，默认 5000（系统错误）
        data: 额外数据，默认为 None
        status_code: HTTP 状态码，默认 200（业务错误不引起 5xx）

    Returns:
        FastAPI JSONResponse
    """
    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder({
            "code": code,
            "message": message,
            "data": data,
        }),
    )
