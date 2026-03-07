<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <div class="logo">
          <span class="logo-icon">🤖</span>
          <span class="logo-text">Mozart AI ERP</span>
        </div>
        <p class="subtitle">AI原生企业资源管理系统</p>
      </div>

      <t-tabs v-model="activeTab" theme="normal">
        <t-tab-panel value="login" label="登录">
          <t-form
            :data="loginForm"
            :rules="loginRules"
            ref="loginFormRef"
            @submit="handleLogin"
          >
            <t-form-item name="username">
              <t-input
                v-model="loginForm.username"
                placeholder="用户名"
                clearable
                size="large"
              >
                <template #prefix-icon>
                  <t-icon name="user" />
                </template>
              </t-input>
            </t-form-item>
            
            <t-form-item name="password">
              <t-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                clearable
                size="large"
              >
                <template #prefix-icon>
                  <t-icon name="lock-on" />
                </template>
              </t-input>
            </t-form-item>

            <t-form-item>
              <t-button
                theme="primary"
                type="submit"
                size="large"
                block
                :loading="authStore.loading"
              >
                登录
              </t-button>
            </t-form-item>
          </t-form>

          <div class="demo-accounts">
            <p class="demo-title">测试账号</p>
            <div class="account-list">
              <t-tag
                v-for="account in demoAccounts"
                :key="account.username"
                theme="primary"
                variant="outline"
                class="account-tag"
                @click="fillDemoAccount(account)"
              >
                {{ account.label }}
              </t-tag>
            </div>
          </div>
        </t-tab-panel>

        <t-tab-panel value="register" label="注册">
          <t-form
            :data="registerForm"
            :rules="registerRules"
            ref="registerFormRef"
            @submit="handleRegister"
          >
            <t-form-item name="username">
              <t-input
                v-model="registerForm.username"
                placeholder="用户名"
                clearable
                size="large"
              >
                <template #prefix-icon>
                  <t-icon name="user" />
                </template>
              </t-input>
            </t-form-item>

            <t-form-item name="email">
              <t-input
                v-model="registerForm.email"
                placeholder="邮箱"
                clearable
                size="large"
              >
                <template #prefix-icon>
                  <t-icon name="mail" />
                </template>
              </t-input>
            </t-form-item>

            <t-form-item name="password">
              <t-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码（至少6位）"
                clearable
                size="large"
              >
                <template #prefix-icon>
                  <t-icon name="lock-on" />
                </template>
              </t-input>
            </t-form-item>

            <t-form-item name="confirmPassword">
              <t-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                clearable
                size="large"
              >
                <template #prefix-icon>
                  <t-icon name="lock-on" />
                </template>
              </t-input>
            </t-form-item>

            <t-form-item name="display_name">
              <t-input
                v-model="registerForm.display_name"
                placeholder="显示名称（可选）"
                clearable
                size="large"
              >
                <template #prefix-icon>
                  <t-icon name="usercircle" />
                </template>
              </t-input>
            </t-form-item>

            <t-form-item>
              <t-button
                theme="success"
                type="submit"
                size="large"
                block
                :loading="authStore.loading"
              >
                注册
              </t-button>
            </t-form-item>
          </t-form>
        </t-tab-panel>
      </t-tabs>

      <div class="login-footer">
        <p>AI 驱动的新一代企业管理系统</p>
      </div>
    </div>

    <!-- 错误提示 -->
    <t-message v-if="authStore.error" theme="error" duration={3000}>
      {{ authStore.error }}
    </t-message>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const loginFormRef = ref()
const registerFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  display_name: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, message: '用户名至少3个字符' }
  ],
  email: [
    { required: true, message: '请输入邮箱' },
    { email: true, message: '请输入有效的邮箱地址' }
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码至少6个字符' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码' },
    {
      validator: (val: string) => val === registerForm.password,
      message: '两次密码输入不一致'
    }
  ]
}

const demoAccounts = [
  { label: '管理员', username: 'admin', password: 'admin123' },
  { label: '张三', username: 'zhangsan', password: '123456' },
  { label: '李四', username: 'lisi', password: '123456' },
  { label: '王五', username: 'wangwu', password: '123456' }
]

const fillDemoAccount = (account: { username: string; password: string }) => {
  loginForm.username = account.username
  loginForm.password = account.password
}

const handleLogin = async () => {
  const valid = await loginFormRef.value?.validate()
  if (valid !== true) return

  const success = await authStore.login(loginForm.username, loginForm.password)
  if (success) {
    MessagePlugin.success('登录成功！')
    router.push('/dashboard')
  }
}

const handleRegister = async () => {
  const valid = await registerFormRef.value?.validate()
  if (valid !== true) return

  const success = await authStore.register(
    registerForm.username,
    registerForm.email,
    registerForm.password,
    registerForm.display_name
  )
  
  if (success) {
    MessagePlugin.success('注册成功！')
    router.push('/dashboard')
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;

  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 8px;

    .logo-icon {
      font-size: 40px;
    }

    .logo-text {
      font-size: 24px;
      font-weight: 700;
      color: #333;
    }
  }

  .subtitle {
    color: #666;
    font-size: 14px;
  }
}

.demo-accounts {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;

  .demo-title {
    font-size: 12px;
    color: #999;
    margin-bottom: 12px;
    text-align: center;
  }

  .account-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
  }

  .account-tag {
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
  }
}

.login-footer {
  margin-top: 24px;
  text-align: center;

  p {
    font-size: 12px;
    color: #999;
  }
}

:deep(.t-tabs__nav) {
  margin-bottom: 24px;
}

:deep(.t-form__item) {
  margin-bottom: 20px;
}
</style>
