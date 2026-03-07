"""
贡献系统API测试
"""

import pytest
from fastapi import status


class TestContributionAPI:
    """贡献系统API测试类"""
    
    def test_submit_contribution_purchase(self, client):
        """测试提交采购贡献"""
        # 先创建Actor
        actor_data = {
            "display_name": "采购员",
            "actor_type": "human"
        }
        actor_response = client.post("/api/v1/actors/", json=actor_data)
        actor_id = actor_response.json()["id"]
        
        # 提交贡献
        contribution_data = {
            "actor_id": actor_id,
            "contribution_type": "purchase_saving",
            "content": "采购土豆20斤，节省了30%",
            "details": {
                "item": "土豆",
                "quantity": 20,
                "original_price": 50,
                "actual_price": 35,
                "saving": 300
            },
            "estimated_value": 90
        }
        
        response = client.post("/api/v1/contributions/", json=contribution_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["contribution_type"] == "purchase_saving"
        assert data["estimated_value"] == 90
    
    def test_submit_contribution_sales(self, client):
        """测试提交销售贡献"""
        # 创建Actor
        actor_data = {
            "display_name": "销售员",
            "actor_type": "human"
        }
        actor_response = client.post("/api/v1/actors/", json=actor_data)
        actor_id = actor_response.json()["id"]
        
        # 提交销售贡献
        contribution_data = {
            "actor_id": actor_id,
            "contribution_type": "sales",
            "content": "完成一笔销售订单",
            "details": {
                "product": "企业服务",
                "amount": 10000,
                "profit_margin": 0.3
            },
            "estimated_value": 1500  # 10000 * 0.3 * 0.5
        }
        
        response = client.post("/api/v1/contributions/", json=contribution_data)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_list_contributions(self, client):
        """测试获取贡献列表"""
        # 创建Actor
        actor_data = {
            "display_name": "贡献者",
            "actor_type": "human"
        }
        actor_response = client.post("/api/v1/actors/", json=actor_data)
        actor_id = actor_response.json()["id"]
        
        # 提交多个贡献
        for i in range(3):
            contribution_data = {
                "actor_id": actor_id,
                "contribution_type": "knowledge_sharing",
                "content": f"分享知识{i}",
                "estimated_value": 50
            }
            client.post("/api/v1/contributions/", json=contribution_data)
        
        # 获取列表
        response = client.get(f"/api/v1/contributions/?actor_id={actor_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data) >= 3
    
    def test_verify_contribution(self, client):
        """测试验证贡献"""
        # 创建Actor和贡献
        actor_data = {
            "display_name": "验证测试",
            "actor_type": "human"
        }
        actor_response = client.post("/api/v1/actors/", json=actor_data)
        actor_id = actor_response.json()["id"]
        
        contribution_data = {
            "actor_id": actor_id,
            "contribution_type": "purchase_saving",
            "content": "测试贡献",
            "estimated_value": 100
        }
        contribution_response = client.post("/api/v1/contributions/", json=contribution_data)
        contribution_id = contribution_response.json()["id"]
        
        # 验证贡献
        verify_data = {
            "actual_value": 95,
            "notes": "核实无误"
        }
        response = client.post(
            f"/api/v1/contributions/{contribution_id}/verify",
            json=verify_data
        )
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_get_contribution_statistics(self, client):
        """测试获取贡献统计"""
        # 创建Actor和贡献
        actor_data = {
            "display_name": "统计测试",
            "actor_type": "human"
        }
        actor_response = client.post("/api/v1/actors/", json=actor_data)
        actor_id = actor_response.json()["id"]
        
        # 提交不同类型的贡献
        contribution_types = ["purchase_saving", "sales", "knowledge_sharing"]
        for ctype in contribution_types:
            contribution_data = {
                "actor_id": actor_id,
                "contribution_type": ctype,
                "content": f"{ctype}贡献",
                "estimated_value": 100
            }
            client.post("/api/v1/contributions/", json=contribution_data)
        
        # 获取统计
        response = client.get(f"/api/v1/contributions/statistics/{actor_id}")
        
        assert response.status_code == status.HTTP_200_OK
