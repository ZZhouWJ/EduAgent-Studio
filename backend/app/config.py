"""
配置管理模块。

所有配置从环境变量读取，不允许硬编码真实密码。
使用 pydantic-settings 自动解析环境变量。
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局配置，来源为环境变量。"""

    # --- 应用信息 ---
    app_name: str = Field(default="EduAgent Studio", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")

    # --- 数据库配置 ---
    db_host: str = Field(default="127.0.0.1", alias="DB_HOST")
    db_port: int = Field(default=3306, alias="DB_PORT")
    db_user: str = Field(default="root", alias="DB_USER")
    db_password: str = Field(default="", alias="DB_PASSWORD")
    db_name: str = Field(default="ai_collab_audit_system", alias="DB_NAME")

    # --- Redis 配置 ---
    redis_url: str = Field(default="redis://127.0.0.1:6379/0", alias="REDIS_URL")

    # --- 服务器配置 ---
    server_host: str = Field(default="0.0.0.0", alias="SERVER_HOST")
    server_port: int = Field(default=8000, alias="SERVER_PORT")

    # --- LLM 配置 ---
    llm_provider: str = Field(default="openai_compatible", alias="LLM_PROVIDER")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(default="https://api.deepseek.com/v1", alias="LLM_BASE_URL")
    llm_model: str = Field(default="deepseek-chat", alias="LLM_MODEL")

    # --- 讯飞星火配置（当 LLM_PROVIDER=iflytek 时生效）---
    iflytek_app_id: str = Field(default="", alias="IFLYTEK_APP_ID")
    iflytek_api_key: str = Field(default="", alias="IFLYTEK_API_KEY")
    iflytek_api_secret: str = Field(default="", alias="IFLYTEK_API_SECRET")
    iflytek_doc_id: str = Field(default="", alias="IFLYTEK_DOC_ID")

    # --- PostgreSQL 配置（pgvector） ---
    postgres_url: str = Field(default="", alias="POSTGRES_URL")

    # --- 应用数据目录 ---
    app_data_dir: str = Field(default="data", alias="APP_DATA_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @property
    def db_url(self) -> str:
        """返回 PyMySQL 连接参数元组（兼容方式）。"""
        return {
            "host": self.db_host,
            "port": self.db_port,
            "user": self.db_user,
            "password": self.db_password,
            "database": self.db_name,
            "charset": "utf8mb4",
        }

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    def llm_config(self, model_name: str = None) -> "LLMConfig":
        """返回当前 LLM 配置。"""
        from app.llm.gateway import LLMConfig as LLMConfigCls
        return LLMConfigCls(
            model_id=0,
            model_name=model_name or self.llm_model,
            provider=self.llm_provider,
            api_key=self.llm_api_key,
            base_url=self.llm_base_url,
            temperature=0.7,
            max_tokens=2048,
            timeout=60,
            api_secret=self.iflytek_api_secret,
            app_id=self.iflytek_app_id,
        )


@lru_cache()
def get_settings() -> Settings:
    """单例获取配置实例。"""
    return Settings()
