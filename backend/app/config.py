"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "Mozart AI ERP"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # 数据库配置
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis配置
    REDIS_URL: str
    REDIS_PASSWORD: str = ""

    # DeepSeek API配置
    DEEPSEEK_API_KEY: str
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_MAX_TOKENS: int = 2000
    DEEPSEEK_TEMPERATURE: float = 0.7

    # OCR服务配置
    TENCENT_SECRET_ID: str = ""
    TENCENT_SECRET_KEY: str = ""
    TENCENT_REGION: str = "ap-guangzhou"

    BAIDU_API_KEY: str = ""
    BAIDU_SECRET_KEY: str = ""

    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,pdf"

    # CORS配置
    CORS_ORIGINS: str = "http://localhost:5173"
    CORS_ALLOW_CREDENTIALS: bool = True

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # 缓存配置
    CACHE_TTL: int = 3600
    CACHE_PREFIX: str = "mozart:"

    @property
    def cors_origins_list(self) -> List[str]:
        """获取CORS origins列表"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        """获取允许的文件扩展名列表"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局配置实例
settings = Settings()
