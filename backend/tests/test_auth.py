"""
认证API测试
"""

import pytest
from fastapi import status


class TestAuthAPI:
    """认证API测试类"""
    
    def test_register_success(self, client, test_user_data):
        """测试用户注册成功"""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == test_user_data["username"]
        assert data["user"]["email"] == test_user_data["email"]
    
    def test_register_duplicate_username(self, client, test_user_data):
        """测试重复用户名注册"""
        # 第一次注册
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 第二次注册（相同用户名）
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "用户名已存在" in response.json()["detail"]
    
    def test_register_duplicate_email(self, client, test_user_data):
        """测试重复邮箱注册"""
        # 第一次注册
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 第二次注册（相同邮箱，不同用户名）
        new_user_data = test_user_data.copy()
        new_user_data["username"] = "anotheruser"
        
        response = client.post("/api/v1/auth/register", json=new_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "邮箱已存在" in response.json()["detail"]
    
    def test_login_success(self, client, test_user_data):
        """测试登录成功"""
        # 先注册
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == test_user_data["username"]
    
    def test_login_wrong_password(self, client, test_user_data):
        """测试密码错误"""
        # 先注册
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # 登录（错误密码）
        login_data = {
            "username": test_user_data["username"],
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """测试登录不存在的用户"""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user(self, client, test_user_data):
        """测试获取当前用户信息"""
        # 注册并获取令牌
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        token = register_response.json()["access_token"]
        
        # 获取当前用户
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
    
    def test_get_current_user_without_token(self, client):
        """测试未提供令牌获取用户信息"""
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, client, test_user_data):
        """测试刷新令牌"""
        # 注册并获取令牌
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        refresh_token = register_response.json()["refresh_token"]
        
        # 刷新令牌
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_change_password(self, client, test_user_data):
        """测试修改密码"""
        # 注册并获取令牌
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        token = register_response.json()["access_token"]
        
        # 修改密码
        change_password_data = {
            "old_password": test_user_data["password"],
            "new_password": "newpassword123"
        }
        response = client.post(
            "/api/v1/auth/change-password",
            json=change_password_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # 用新密码登录
        login_data = {
            "username": test_user_data["username"],
            "password": "newpassword123"
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        
        assert login_response.status_code == status.HTTP_200_OK
    
    def test_change_password_wrong_old(self, client, test_user_data):
        """测试修改密码（旧密码错误）"""
        # 注册并获取令牌
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        token = register_response.json()["access_token"]
        
        # 修改密码（错误旧密码）
        change_password_data = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = client.post(
            "/api/v1/auth/change-password",
            json=change_password_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
