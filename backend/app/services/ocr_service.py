"""
OCR服务 - 支持腾讯云OCR和百度OCR

用于识别发票、单据等图片中的文字信息
"""

import base64
import httpx
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from app.config import settings


class OCRProvider(ABC):
    """OCR服务提供者基类"""
    
    @abstractmethod
    async def recognize_text(self, image_data: bytes) -> Dict[str, Any]:
        """
        识别图片中的文字
        
        Args:
            image_data: 图片二进制数据
        
        Returns:
            识别结果
        """
        pass
    
    @abstractmethod
    async def recognize_invoice(self, image_data: bytes) -> Dict[str, Any]:
        """
        识别发票信息
        
        Args:
            image_data: 图片二进制数据
        
        Returns:
            发票识别结果
        """
        pass


class TencentOCRProvider(OCRProvider):
    """腾讯云OCR服务"""
    
    def __init__(self):
        self.secret_id = settings.TENCENT_SECRET_ID
        self.secret_key = settings.TENCENT_SECRET_KEY
        self.region = settings.TENCENT_REGION
        self.base_url = f"https://ocr.{self.region}.tencentcloudapi.com"
    
    def _sign_request(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """
        签名请求
        
        简化版本，实际使用时需要完整的腾讯云签名算法
        """
        import hashlib
        import hmac
        import time
        
        timestamp = int(time.time())
        # 这里需要实现完整的腾讯云签名算法
        # 简化版本，实际使用时请参考腾讯云文档
        headers = {
            "Authorization": f"TC3-HMAC-SHA256 Credential={self.secret_id}",
            "X-TC-Action": payload.get("Action", ""),
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": "2018-11-19",
            "Content-Type": "application/json"
        }
        
        return headers
    
    async def recognize_text(self, image_data: bytes) -> Dict[str, Any]:
        """通用文字识别"""
        if not self.secret_id or not self.secret_key:
            return self._mock_response("通用文字识别")
        
        try:
            # Base64编码图片
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            
            # 构建请求
            payload = {
                "Action": "GeneralBasicOCR",
                "ImageBase64": image_base64,
                "Version": "2018-11-19"
            }
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=self._sign_request(payload),
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "text": self._extract_text(result),
                        "details": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"OCR请求失败: {response.status_code}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR识别异常: {str(e)}"
            }
    
    async def recognize_invoice(self, image_data: bytes) -> Dict[str, Any]:
        """发票识别"""
        if not self.secret_id or not self.secret_key:
            return self._mock_invoice_response()
        
        try:
            # Base64编码图片
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            
            # 构建请求
            payload = {
                "Action": "VatInvoiceOCR",
                "ImageBase64": image_base64,
                "Version": "2018-11-19"
            }
            
            # 发送请求
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=self._sign_request(payload),
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "invoice": self._extract_invoice(result),
                        "details": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"发票识别失败: {response.status_code}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"发票识别异常: {str(e)}"
            }
    
    def _extract_text(self, result: Dict[str, Any]) -> str:
        """提取识别的文字"""
        text_items = result.get("Response", {}).get("TextDetections", [])
        return "\n".join([item.get("DetectedText", "") for item in text_items])
    
    def _extract_invoice(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """提取发票信息"""
        invoice = result.get("Response", {}).get("VatInvoiceInfos", [{}])[0]
        return {
            "code": invoice.get("Code", ""),  # 发票代码
            "number": invoice.get("Number", ""),  # 发票号码
            "date": invoice.get("Date", ""),  # 开票日期
            "buyer": invoice.get("Buyer", ""),  # 购买方名称
            "seller": invoice.get("Seller", ""),  # 销售方名称
            "total": invoice.get("Total", ""),  # 价税合计
            "tax": invoice.get("Tax", ""),  # 税额
            "items": invoice.get("Items", [])  # 商品明细
        }
    
    def _mock_response(self, text_type: str) -> Dict[str, Any]:
        """模拟响应（当API密钥未配置时）"""
        return {
            "success": True,
            "text": f"[模拟OCR识别结果 - {text_type}]",
            "details": {
                "note": "OCR服务未配置，返回模拟数据"
            }
        }
    
    def _mock_invoice_response(self) -> Dict[str, Any]:
        """模拟发票识别响应"""
        return {
            "success": True,
            "invoice": {
                "code": "1234567890",
                "number": "12345678",
                "date": "2026-03-06",
                "buyer": "示例公司",
                "seller": "供应商公司",
                "total": "1000.00",
                "tax": "130.00",
                "items": [
                    {
                        "name": "示例商品",
                        "quantity": "10",
                        "price": "100.00",
                        "amount": "1000.00"
                    }
                ]
            },
            "details": {
                "note": "OCR服务未配置，返回模拟数据"
            }
        }


class BaiduOCRProvider(OCRProvider):
    """百度OCR服务"""
    
    def __init__(self):
        self.api_key = settings.BAIDU_API_KEY
        self.secret_key = settings.BAIDU_SECRET_KEY
        self.base_url = "https://aip.baidubce.com/rest/2.0/ocr/v1"
        self.access_token = None
    
    async def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self.access_token:
            return self.access_token
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params)
            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                return self.access_token
        
        return ""
    
    async def recognize_text(self, image_data: bytes) -> Dict[str, Any]:
        """通用文字识别"""
        if not self.api_key or not self.secret_key:
            return self._mock_response("通用文字识别")
        
        try:
            # Base64编码图片
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            
            # 获取访问令牌
            access_token = await self._get_access_token()
            
            # 发送请求
            url = f"{self.base_url}/general_basic?access_token={access_token}"
            params = {"image": image_base64}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=params, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "text": self._extract_text(result),
                        "details": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"OCR请求失败: {response.status_code}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR识别异常: {str(e)}"
            }
    
    async def recognize_invoice(self, image_data: bytes) -> Dict[str, Any]:
        """发票识别"""
        if not self.api_key or not self.secret_key:
            return self._mock_invoice_response()
        
        try:
            # Base64编码图片
            image_base64 = base64.b64encode(image_data).decode("utf-8")
            
            # 获取访问令牌
            access_token = await self._get_access_token()
            
            # 发送请求
            url = f"{self.base_url}/vat_invoice?access_token={access_token}"
            params = {"image": image_base64}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=params, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "invoice": self._extract_invoice(result),
                        "details": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"发票识别失败: {response.status_code}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"发票识别异常: {str(e)}"
            }
    
    def _extract_text(self, result: Dict[str, Any]) -> str:
        """提取识别的文字"""
        words = result.get("words_result", [])
        return "\n".join([item.get("words", "") for item in words])
    
    def _extract_invoice(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """提取发票信息"""
        words_result = result.get("words_result", {})
        return {
            "code": words_result.get("InvoiceCode", ""),  # 发票代码
            "number": words_result.get("InvoiceNum", ""),  # 发票号码
            "date": words_result.get("InvoiceDate", ""),  # 开票日期
            "buyer": words_result.get("PurchaserName", ""),  # 购买方名称
            "seller": words_result.get("SellerName", ""),  # 销售方名称
            "total": words_result.get("TotalAmount", ""),  # 价税合计
            "tax": words_result.get("TotalTax", ""),  # 税额
            "items": words_result.get("CommodityName", [])  # 商品明细
        }
    
    def _mock_response(self, text_type: str) -> Dict[str, Any]:
        """模拟响应（当API密钥未配置时）"""
        return {
            "success": True,
            "text": f"[模拟OCR识别结果 - {text_type}]",
            "details": {
                "note": "OCR服务未配置，返回模拟数据"
            }
        }
    
    def _mock_invoice_response(self) -> Dict[str, Any]:
        """模拟发票识别响应"""
        return {
            "success": True,
            "invoice": {
                "code": "1234567890",
                "number": "12345678",
                "date": "2026-03-06",
                "buyer": "示例公司",
                "seller": "供应商公司",
                "total": "1000.00",
                "tax": "130.00",
                "items": [
                    {
                        "name": "示例商品",
                        "quantity": "10",
                        "price": "100.00",
                        "amount": "1000.00"
                    }
                ]
            },
            "details": {
                "note": "OCR服务未配置，返回模拟数据"
            }
        }


class OCRService:
    """OCR服务"""
    
    def __init__(self, provider: str = "tencent"):
        """
        初始化OCR服务
        
        Args:
            provider: 服务提供者（"tencent" 或 "baidu"）
        """
        self.provider_name = provider
        
        if provider == "tencent":
            self.provider = TencentOCRProvider()
        elif provider == "baidu":
            self.provider = BaiduOCRProvider()
        else:
            raise ValueError(f"不支持的OCR服务提供者: {provider}")
    
    async def recognize_text(self, image_data: bytes) -> Dict[str, Any]:
        """通用文字识别"""
        return await self.provider.recognize_text(image_data)
    
    async def recognize_invoice(self, image_data: bytes) -> Dict[str, Any]:
        """发票识别"""
        return await self.provider.recognize_invoice(image_data)
    
    async def recognize_purchase_document(self, image_data: bytes) -> Dict[str, Any]:
        """
        识别采购单据
        
        从图片中提取采购相关信息
        """
        # 先尝试发票识别
        invoice_result = await self.recognize_invoice(image_data)
        
        if invoice_result.get("success"):
            invoice = invoice_result.get("invoice", {})
            
            # 转换为采购贡献格式
            purchase_data = {
                "type": "purchase",
                "success": True,
                "details": {
                    "document_type": "invoice",
                    "seller": invoice.get("seller", ""),
                    "total": float(invoice.get("total", 0)),
                    "items": invoice.get("items", [])
                },
                "contribution_value": self._calculate_purchase_value(invoice)
            }
            
            return purchase_data
        
        # 如果发票识别失败，使用通用文字识别
        text_result = await self.recognize_text(image_data)
        
        if text_result.get("success"):
            return {
                "type": "purchase",
                "success": True,
                "details": {
                    "document_type": "text",
                    "text": text_result.get("text", "")
                },
                "note": "请人工确认采购信息"
            }
        
        return {
            "type": "purchase",
            "success": False,
            "error": "无法识别图片内容"
        }
    
    def _calculate_purchase_value(self, invoice: Dict[str, Any]) -> float:
        """
        计算采购贡献价值
        
        简化版本，实际可以根据采购金额、供应商信息等计算
        """
        total = float(invoice.get("total", 0))
        # 假设节省了10%
        saving_rate = 0.1
        return total * saving_rate
