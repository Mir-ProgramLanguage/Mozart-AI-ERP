"""
Actor管理API测试
"""

import pytest
from fastapi import status


class TestActorAPI:
    """Actor管理API测试类"""
    
    def test_create_actor_success(self, client):
        """测试创建Actor成功"""
        actor_data = {
            "display_name": "测试Actor",
            "actor_type": "human",
            "capabilities": {
                "开发": 0.9,
                "产品": 0.8
            }
        }
        
        response = client.post("/api/v1/actors/", json=actor_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["display_name"] == actor_data["display_name"]
        assert data["actor_type"] == "human"
        assert data["capabilities"]["开发"] == 0.9
    
    def test_create_duplicate_actor(self, client):
        """测试创建重复Actor"""
        actor_data = {
            "display_name": "重复Actor",
            "actor_type": "human"
        }
        
        # 第一次创建
        client.post("/api/v1/actors/", json=actor_data)
        
        # 第二次创建（相同名称）
        response = client.post("/api/v1/actors/", json=actor_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_actor_by_id(self, client):
        """测试获取Actor详情"""
        # 创建Actor
        actor_data = {
            "display_name": "测试Actor",
            "actor_type": "human"
        }
        create_response = client.post("/api/v1/actors/", json=actor_data)
        actor_id = create_response.json()["id"]
        
        # 获取Actor
        response = client.get(f"/api/v1/actors/{actor_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == actor_id
        assert data["display_name"] == actor_data["display_name"]
    
    def test_get_nonexistent_actor(self, client):
        """测试获取不存在的Actor"""
        response = client.get("/api/v1/actors/00000000-0000-0000-0000-000000000999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_actors(self, client):
        """测试获取Actor列表"""
        # 创建多个Actor
        for i in range(3):
            actor_data = {
                "display_name": f"测试Actor{i}",
                "actor_type": "human"
            }
            client.post("/api/v1/actors/", json=actor_data)
        
        # 获取列表
        response = client.get("/api/v1/actors/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data) >= 3
    
    def test_update_actor_capabilities(self, client):
        """测试更新Actor能力"""
        # 创建Actor
        actor_data = {
            "display_name": "测试Actor",
            "actor_type": "human",
            "capabilities": {"开发": 0.8}
        }
        create_response = client.post("/api/v1/actors/", json=actor_data)
        actor_id = create_response.json()["id"]
        
        # 更新能力
        update_data = {
            "capabilities": {
                "开发": 0.9,
                "产品": 0.7
            }
        }
        response = client.put(f"/api/v1/actors/{actor_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["capabilities"]["开发"] == 0.9
        assert data["capabilities"]["产品"] == 0.7
    
    def test_get_leaderboard(self, client):
        """测试获取贡献排行榜"""
        # 创建多个Actor并设置贡献值
        for i in range(3):
            actor_data = {
                "display_name": f"排行榜Actor{i}",
                "actor_type": "human"
            }
            create_response = client.post("/api/v1/actors/", json=actor_data)
            actor_id = create_response.json()["id"]
            
            # 更新贡献值
            update_data = {
                "total_contributions": (3 - i) * 1000  # 第一个最高
            }
            client.put(f"/api/v1/actors/{actor_id}", json=update_data)
        
        # 获取排行榜
        response = client.get("/api/v1/actors/leaderboard")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data) >= 3
        # 验证按贡献值排序
        if len(data) >= 2:
            assert data[0]["total_contributions"] >= data[1]["total_contributions"]
    
    def test_create_ai_agent(self, client):
        """测试创建AI Agent"""
        actor_data = {
            "display_name": "AI助手001",
            "actor_type": "ai_agent",
            "ai_config": {
                "role": "文案助手",
                "description": "擅长文案撰写和内容创作",
                "capabilities": ["文案", "写作", "创意"],
                "model": "deepseek"
            }
        }
        
        response = client.post("/api/v1/actors/", json=actor_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["actor_type"] == "ai_agent"
