<template>
  <t-config-provider :global-config="globalConfig">
    <!-- 未登录时显示登录页面 -->
    <template v-if="!authStore.isAuthenticated">
      <router-view />
    </template>
    
    <!-- 已登录时显示主布局 -->
    <t-layout v-else class="app-layout">
      <t-aside class="app-aside">
        <div class="logo">
          <span class="logo-icon">🤖</span>
          <span class="logo-text">Mozart AI</span>
        </div>
        <t-menu theme="dark" :value="activeMenu" @change="onMenuChange">
          <t-menu-item value="dashboard">
            <template #icon>
              <t-icon name="dashboard" />
            </template>
            仪表盘
          </t-menu-item>
          <t-menu-item value="chat">
            <template #icon>
              <t-icon name="chat" />
            </template>
            我的工作
          </t-menu-item>
          <t-menu-item value="tasks">
            <template #icon>
              <t-icon name="task" />
            </template>
            任务看板
          </t-menu-item>
          <t-menu-item value="contributions">
            <template #icon>
              <t-icon name="chart-bar" />
            </template>
            贡献记录
          </t-menu-item>
          <t-menu-item value="rewards">
            <template #icon>
              <t-icon name="gift" />
            </template>
            回报中心
          </t-menu-item>
          <t-menu-item value="ai-agents">
            <template #icon>
              <t-icon name="robot" />
            </template>
            AI 员工
          </t-menu-item>
        </t-menu>
        
        <!-- 底部用户信息 -->
        <div class="user-section">
          <t-dropdown placement="rightTop" @click="handleUserAction">
            <div class="user-info">
              <t-avatar size="small">{{ authStore.displayName?.charAt(0)?.toUpperCase() }}</t-avatar>
              <span class="user-name">{{ authStore.displayName }}</span>
            </div>
            <template #dropdown>
              <t-dropdown-menu>
                <t-dropdown-item @click="showProfile = true">
                  <t-icon name="user-circle" /> 个人信息
                </t-dropdown-item>
                <t-dropdown-item @click="handleLogout">
                  <t-icon name="poweroff" /> 退出登录
                </t-dropdown-item>
              </t-dropdown-menu>
            </template>
          </t-dropdown>
        </div>
      </t-aside>
      <t-layout>
        <t-header class="app-header">
          <div class="header-left">
            <span class="page-title">{{ pageTitle }}</span>
          </div>
          <div class="header-right">
            <t-tooltip content="刷新数据" placement="bottom">
              <t-button variant="text" shape="circle" @click="refreshData">
                <t-icon name="refresh" />
              </t-button>
            </t-tooltip>
            <t-badge :count="notificationCount" :max-count="99">
              <t-button variant="text" shape="circle" @click="showNotifications = true">
                <t-icon name="notification" />
              </t-button>
            </t-badge>
          </div>
        </t-header>
        <t-content class="app-content">
          <router-view />
        </t-content>
      </t-layout>
    </t-layout>

    <!-- 通知抽屉 -->
    <t-drawer
      v-model:visible="showNotifications"
      header="通知中心"
      :footer="false"
      size="400px"
    >
      <t-list :split="true">
        <t-list-item v-for="notification in notifications" :key="notification.id">
          <t-list-item-meta>
            <template #title>{{ notification.title }}</template>
            <template #description>
              <div class="notification-content">{{ notification.message }}</div>
              <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
            </template>
          </t-list-item-meta>
        </t-list-item>
        <t-list-item v-if="notifications.length === 0">
          <t-empty description="暂无通知" />
        </t-list-item>
      </t-list>
    </t-drawer>
  </t-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { request } from '@/api/request'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const chatStore = useChatStore()

const globalConfig = {
  classPrefix: 't'
}

const showNotifications = ref(false)
const showProfile = ref(false)
const notifications = ref<any[]>([])
const notificationCount = ref(0)

const activeMenu = computed(() => {
  const path = route.path.split('/')[1]
  return path || 'dashboard'
})

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    chat: '我的工作',
    dashboard: '仪表盘',
    'ai-agents': 'AI 员工管理',
    tasks: '任务看板',
    contributions: '贡献记录',
    rewards: '回报中心'
  }
  return titles[activeMenu.value] || 'AI ERP'
})

const onMenuChange = (value: string) => {
  router.push(`/${value}`)
}

const handleUserAction = (data: any) => {
  // 处理下拉菜单点击
}

const handleLogout = async () => {
  await authStore.logout()
  MessagePlugin.success('已退出登录')
  router.push('/login')
}

const refreshData = async () => {
  await chatStore.fetchStats()
  MessagePlugin.success('数据已刷新')
}

const fetchNotifications = async () => {
  try {
    const response = await request.get('/notifications/', { params: { limit: 10 } })
    notifications.value = response.notifications || []
    notificationCount.value = response.unread_count || 0
  } catch (e) {
    console.error('Failed to fetch notifications:', e)
  }
}

const formatTime = (dateStr: string) => {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

onMounted(() => {
  // 获取初始数据
  if (authStore.isAuthenticated) {
    chatStore.fetchStats()
    fetchNotifications()
  }
})
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f5f7fa;
}

.app-layout {
  height: 100vh;
}

.app-aside {
  background: #001529;
  width: 200px !important;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .logo-icon {
      font-size: 24px;
    }
  }

  .t-menu {
    background: transparent;
    flex: 1;
  }

  .user-section {
    padding: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);

    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #fff;
      cursor: pointer;
      padding: 8px;
      border-radius: 8px;
      transition: background 0.2s;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      .user-name {
        font-size: 14px;
      }
    }
  }
}

.app-header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  height: 64px;

  .header-left {
    .page-title {
      font-size: 18px;
      font-weight: 500;
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.app-content {
  padding: 24px;
  overflow: auto;
}

.notification-content {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.notification-time {
  font-size: 12px;
  color: #999;
}
</style>
