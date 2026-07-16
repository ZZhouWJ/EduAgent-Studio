"""
配置管理模块。

所有配置从环境变量读取，不允许硬编码真实密码。
使用 pydantic-settings 自动解析环境变量。
"""

from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局配置，来源为环境变量。"""

    # --- 应用信息 ---
    app_name: str = Field(default="EduAgent Studio", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    api_prefix: str = Field(default="/api", alias="API_PREFIX")

    # --- 安全配置 ---
    jwt_secret_key: str = Field(
        default="dev-secret-key-change-before-production",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = Field(
        default="HS256",
        alias="JWT_ALGORITHM",
    )
    jwt_expire_minutes: int = Field(
        default=1440,
        gt=0,
        le=10080,
        alias="JWT_EXPIRE_MINUTES",
    )
    cors_origins: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173",
        alias="CORS_ORIGINS",
    )

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
    llm_provider: Literal[
        "mock",
        "openai_compatible",
        "openai",
        "deepseek",
        "qwen",
        "minimax",
        "iflytek",
    ] = Field(default="openai_compatible", alias="LLM_PROVIDER")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_base_url: str = Field(default="https://api.deepseek.com/v1", alias="LLM_BASE_URL")
    llm_model: str = Field(default="deepseek-chat", alias="LLM_MODEL")

    # --- 讯飞星火配置（当 LLM_PROVIDER=iflytek 时生效）---
    iflytek_app_id: str = Field(default="", alias="IFLYTEK_APP_ID")
    iflytek_api_key: str = Field(default="", alias="IFLYTEK_API_KEY")
    iflytek_api_secret: str = Field(default="", alias="IFLYTEK_API_SECRET")
    iflytek_doc_id: str = Field(default="", alias="IFLYTEK_DOC_ID")

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

    @property
    def cors_origin_list(self) -> list[str]:
        """返回去重后的跨域来源列表。"""
        return list(
            dict.fromkeys(
                origin.strip().rstrip("/")
                for origin in self.cors_origins.split(",")
                if origin.strip()
            )
        )

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """生产环境禁止弱 JWT 密钥和任意来源跨域。"""
        if not self.is_production:
            return self

        weak_markers = ("change_me", "change-before-production", "dev-secret")
        if len(self.jwt_secret_key) < 32 or any(
            marker in self.jwt_secret_key.lower() for marker in weak_markers
        ):
            raise ValueError("生产环境 JWT_SECRET_KEY 必须是至少 32 字符的随机密钥")
        if not self.cors_origin_list or "*" in self.cors_origin_list:
            raise ValueError("生产环境 CORS_ORIGINS 必须配置明确的前端来源")
        if self.llm_provider == "mock":
            raise ValueError("生产环境禁止使用 Mock 模型")
        if self.llm_provider == "iflytek":
            if not all((self.iflytek_app_id, self.iflytek_api_key, self.iflytek_api_secret)):
                raise ValueError("生产环境使用讯飞时必须配置 APP_ID、API_KEY 和 API_SECRET")
        elif not self.llm_api_key:
            raise ValueError("生产环境必须配置 LLM_API_KEY")
        return self

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
