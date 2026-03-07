"""
OCR API - 图片识别接口
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from typing import Optional
from app.services.ocr_service import OCRService
from app.core.deps import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/ocr", tags=["OCR识别"])


@router.post("/recognize/text")
async def recognize_text(
    file: UploadFile = File(..., description="图片文件"),
    current_user: User = Depends(get_current_active_user)
):
    """
    通用文字识别
    
    上传图片，识别其中的文字内容
    """
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    # 读取图片数据
    image_data = await file.read()
    
    # 创建OCR服务
    ocr_service = OCRService(provider="tencent")  # 默认使用腾讯云
    
    # 识别文字
    result = await ocr_service.recognize_text(image_data)
    
    return result


@router.post("/recognize/invoice")
async def recognize_invoice(
    file: UploadFile = File(..., description="发票图片"),
    current_user: User = Depends(get_current_active_user)
):
    """
    发票识别
    
    上传发票图片，识别发票信息
    """
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    # 读取图片数据
    image_data = await file.read()
    
    # 创建OCR服务
    ocr_service = OCRService(provider="tencent")
    
    # 识别发票
    result = await ocr_service.recognize_invoice(image_data)
    
    return result


@router.post("/recognize/purchase")
async def recognize_purchase_document(
    file: UploadFile = File(..., description="采购单据图片"),
    current_user: User = Depends(get_current_active_user)
):
    """
    采购单据识别
    
    上传采购单据图片，自动识别并生成贡献记录建议
    """
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    # 读取图片数据
    image_data = await file.read()
    
    # 创建OCR服务
    ocr_service = OCRService(provider="tencent")
    
    # 识别采购单据
    result = await ocr_service.recognize_purchase_document(image_data)
    
    return result


@router.post("/upload-and-contribute")
async def upload_and_contribute(
    file: UploadFile = File(..., description="图片文件"),
    contribution_type: str = "auto",
    current_user: User = Depends(get_current_active_user)
):
    """
    上传图片并自动生成贡献
    
    智能识别图片内容，自动生成贡献记录
    """
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持图片文件"
        )
    
    # 读取图片数据
    image_data = await file.read()
    
    # 创建OCR服务
    ocr_service = OCRService(provider="tencent")
    
    # 根据贡献类型选择识别方式
    if contribution_type == "invoice":
        result = await ocr_service.recognize_invoice(image_data)
    elif contribution_type == "purchase":
        result = await ocr_service.recognize_purchase_document(image_data)
    else:
        # 自动判断，先尝试发票识别，失败则用文字识别
        result = await ocr_service.recognize_invoice(image_data)
        
        if not result.get("success"):
            result = await ocr_service.recognize_text(image_data)
    
    # 添加贡献建议
    result["contribution_suggestion"] = {
        "actor_id": str(current_user.actor_id) if current_user.actor_id else None,
        "created_at": "now",
        "status": "pending_verification"
    }
    
    return result
