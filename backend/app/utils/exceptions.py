"""
基础异常类模块。

定义项目业务异常和系统异常，供 FastAPI 全局异常处理器使用。
禁止在错误信息中暴露密码、API Key 等敏感数据。
"""

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.utils.response import error_response

logger = logging.getLogger(__name__)


class AppException(Exception):
    """业务异常基类。"""

    def __init__(self, message: str, code: int = 4000):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundException(AppException):
    """资源不存在。"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(message=message, code=4003)


class UnauthorizedException(AppException):
    """未授权。"""

    def __init__(self, message: str = "未登录或登录已过期"):
        super().__init__(message=message, code=4002)


class ForbiddenException(AppException):
    """权限不足。"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(message=message, code=4001)


class ValidationException(AppException):
    """参数校验失败。"""

    def __init__(self, message: str = "参数错误"):
        super().__init__(message=message, code=4000)


class ConflictException(AppException):
    """数据冲突（如乐观锁失败）。"""

    def __init__(self, message: str = "数据已被其他用户修改，请刷新后重试"):
        super().__init__(message=message, code=4004)


class DatabaseException(AppException):
    """数据库错误。"""

    def __init__(self, message: str = "数据库操作失败"):
        super().__init__(message=message, code=5002)


def register_exception_handlers(app: FastAPI) -> None:
    """
    注册全局异常处理器到 FastAPI 实例。

    异常处理器将异常转换为统一 JSON 响应格式，
    禁止在错误信息中暴露内部实现细节或敏感数据。
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        status_code = {
            4000: 400,
            4001: 403,
            4002: 401,
            4003: 404,
            4004: 409,
            5002: 503,
        }.get(exc.code, 400)
        return error_response(
            message=exc.message,
            code=exc.code,
            status_code=status_code,
        )

    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
        return error_response(message=exc.message, code=exc.code, status_code=503)

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
        return error_response(
            message="系统内部错误，请稍后重试",
            code=5000,
            status_code=500,
        )
