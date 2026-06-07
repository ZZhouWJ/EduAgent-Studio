"""
FastAPI 应用入口。

Stage-02 仅包含：
- 全局异常处理注册
- /api/health（不依赖数据库）
- /api/health/db（依赖数据库）
- 统一响应格式
"""

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import test_connection
from app.routers import auth, users, projects, tasks, prompts, models, invocations, reviews, artifacts, statistics, logs
from app.utils.exceptions import register_exception_handlers
from app.utils.response import error_response, success_response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="智研协作：面向高校项目协作的 AI 任务生成与质量审计管理系统",
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(projects.router)
    app.include_router(tasks.router)
    app.include_router(prompts.router)
    app.include_router(models.router)
    app.include_router(invocations.router)
    app.include_router(reviews.router)
    app.include_router(artifacts.router)
    app.include_router(statistics.router)
    app.include_router(logs.router)

    @app.get("/")
    async def root() -> dict:
        """根路径，重定向到 /docs。"""
        return success_response(
            data={
                "name": settings.app_name,
                "env": settings.app_env,
                "docs": "/docs",
            },
            message="服务正常运行",
        )

    @app.get(f"{settings.api_prefix}/health")
    async def health_check() -> dict:
        """
        服务健康检查接口（不依赖数据库）。
        检查服务本身是否启动。
        """
        return success_response(
            data={
                "status": "ok",
                "service": settings.app_name,
                "env": settings.app_env,
            },
            message="success",
        )

    @app.get(f"{settings.api_prefix}/health/db")
    async def health_check_db() -> Any:
        """
        数据库健康检查接口（依赖数据库连接）。

        - 数据库连接成功：code=0，data.database="connected"
        - 数据库连接失败：code=5002，data.database="disconnected"
          错误信息不含密码等敏感数据，不导致服务崩溃。
        """
        db_result = test_connection()

        if db_result["connected"]:
            return success_response(
                data={
                    "status": "ok",
                    "database": "connected",
                    "server_version": db_result["server_version"],
                },
                message="数据库连接正常",
            )
        else:
            logger.warning("数据库健康检查失败: %s", db_result["message"])
            return error_response(
                message=db_result["message"],
                code=5002,
                data={
                    "status": "degraded",
                    "database": "disconnected",
                },
            )

    logger.info(
        "FastAPI 应用初始化完成，API Prefix: %s, 环境: %s",
        settings.api_prefix,
        settings.app_env,
    )
    return app


app = create_app()
