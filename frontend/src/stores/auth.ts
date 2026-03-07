import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { request } from '@/api/request'

export interface User {
  id: number
  username: string
  email: string
  actor_id: string | null
  is_active: boolean
  is_superuser: boolean
  created_at: string
  last_login: string | null
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const tokens = ref<AuthTokens | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!tokens.value?.access_token)
  const displayName = computed(() => user.value?.username || 'Guest')
  const actorId = computed(() => user.value?.actor_id)

  // 登录
  const login = async (username: string, password: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await request.post('/auth/login', { username, password })
      
      tokens.value = {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type,
        expires_in: response.expires_in
      }
      
      user.value = response.user
      
      // 存储到 localStorage
      localStorage.setItem('auth_tokens', JSON.stringify(tokens.value))
      localStorage.setItem('auth_user', JSON.stringify(user.value))
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登录失败，请检查用户名和密码'
      return false
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (username: string, email: string, password: string, display_name?: string) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await request.post('/auth/register', {
        username,
        email,
        password,
        display_name: display_name || username
      })
      
      tokens.value = {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type,
        expires_in: response.expires_in
      }
      
      user.value = response.user
      
      localStorage.setItem('auth_tokens', JSON.stringify(tokens.value))
      localStorage.setItem('auth_user', JSON.stringify(user.value))
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.detail || '注册失败'
      return false
    } finally {
      loading.value = false
    }
  }

  // 登出
  const logout = async () => {
    try {
      await request.post('/auth/logout')
    } catch (e) {
      // ignore
    }
    
    user.value = null
    tokens.value = null
    localStorage.removeItem('auth_tokens')
    localStorage.removeItem('auth_user')
  }

  // 刷新 token
  const refreshToken = async () => {
    if (!tokens.value?.refresh_token) return false
    
    try {
      const response = await request.post('/auth/refresh', {
        refresh_token: tokens.value.refresh_token
      })
      
      tokens.value = {
        access_token: response.access_token,
        refresh_token: response.refresh_token,
        token_type: response.token_type,
        expires_in: response.expires_in
      }
      
      localStorage.setItem('auth_tokens', JSON.stringify(tokens.value))
      return true
    } catch (e) {
      logout()
      return false
    }
  }

  // 从 localStorage 恢复状态
  const restoreSession = () => {
    try {
      const savedTokens = localStorage.getItem('auth_tokens')
      const savedUser = localStorage.getItem('auth_user')
      
      if (savedTokens && savedUser) {
        tokens.value = JSON.parse(savedTokens)
        user.value = JSON.parse(savedUser)
        return true
      }
    } catch (e) {
      console.error('Failed to restore session:', e)
    }
    return false
  }

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    if (!tokens.value?.access_token) return null
    
    try {
      const response = await request.get('/auth/me')
      user.value = response
      localStorage.setItem('auth_user', JSON.stringify(user.value))
      return user.value
    } catch (e) {
      return null
    }
  }

  return {
    user,
    tokens,
    loading,
    error,
    isAuthenticated,
    displayName,
    actorId,
    login,
    register,
    logout,
    refreshToken,
    restoreSession,
    fetchCurrentUser
  }
})
