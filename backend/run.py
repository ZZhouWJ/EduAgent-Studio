"""
本地开发启动入口。

使用 uvicorn 启动 FastAPI 应用。
环境变量优先，详见 .env 文件或系统环境变量。

用法：
    python run.py

或使用 uvicorn 直接启动：
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"""

import os
import sys

# 将 backend/ 目录加入 Python 模块搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import get_settings
from app.main import app

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=not settings.is_production,
        log_level="info",
    )
