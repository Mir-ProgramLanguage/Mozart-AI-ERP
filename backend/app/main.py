"""
FastAPI主应用
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine

# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    description="Mozart AI ERP - 原生AI驱动的企业资源管理系统",
    version="1.0.0",
    debug=settings.DEBUG,
)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    Base.metadata.create_all(bind=engine)
    print("[OK] Database initialized")


# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Mozart AI ERP API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 注册路由
from app.api.v1 import ai_core, contributions, actors, tasks, search, unified, auth, ocr, notifications, export

# 认证路由
app.include_router(auth.router, prefix="/api/v1", tags=["认证"])

# OCR识别路由
app.include_router(ocr.router, prefix="/api/v1", tags=["OCR识别"])

# 通知系统路由
app.include_router(notifications.router, prefix="/api/v1", tags=["通知系统"])

# 核心AI路由 - 所有交互都通过这里
app.include_router(ai_core.router, prefix="/api/v1", tags=["AI中枢"])

# 贡献系统路由
app.include_router(contributions.router, prefix="/api/v1", tags=["贡献系统"])

# Actor 管理路由
app.include_router(actors.router, prefix="/api/v1", tags=["Actor管理"])

# 任务管理路由
app.include_router(tasks.router, prefix="/api/v1", tags=["任务管理"])

# 语义搜索路由
app.include_router(search.router, prefix="/api/v1", tags=["语义搜索"])

# 统一接口路由
app.include_router(unified.router, prefix="/api/v1", tags=["统一接口"])

# 数据导出路由
app.include_router(export.router, prefix="/api/v1", tags=["数据导出"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
