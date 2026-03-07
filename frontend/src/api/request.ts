import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'

const instance: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    try {
      const authTokensStr = localStorage.getItem('auth_tokens')
      if (authTokensStr) {
        const authTokens = JSON.parse(authTokensStr)
        if (authTokens.access_token) {
          config.headers.Authorization = `Bearer ${authTokens.access_token}`
        }
      }
    } catch (e) {
      console.error('Failed to parse auth tokens:', e)
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    
    // 401 未授权 - 清除登录状态
    if (status === 401) {
      localStorage.removeItem('auth_tokens')
      localStorage.removeItem('auth_user')
      // 如果不在登录页，跳转到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    // 提取错误信息
    let message = '请求失败'
    if (typeof detail === 'string') {
      message = detail
    } else if (Array.isArray(detail)) {
      message = detail.map((d: any) => d.msg || d.message).join(', ')
    } else if (error.response?.data?.message) {
      message = error.response.data.message
    } else if (error.message) {
      message = error.message
    }
    
    const err = new Error(message) as any
    err.status = status
    err.response = error.response
    return Promise.reject(err)
  }
)

export const request = {
  get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.get(url, config)
  },
  post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.post(url, data, config)
  },
  put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.put(url, data, config)
  },
  patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return instance.patch(url, data, config)
  },
  delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return instance.delete(url, config)
  }
}
