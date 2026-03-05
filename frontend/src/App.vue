<template>
  <t-config-provider :global-config="globalConfig">
    <t-layout class="app-layout">
      <t-aside class="app-aside">
        <div class="logo">
          <span class="logo-icon">🤖</span>
          <span class="logo-text">AI ERP</span>
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
            AI 对话
          </t-menu-item>
          <t-menu-item value="ai-agents">
            <template #icon>
              <t-icon name="robot" />
            </template>
            AI 员工
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
        </t-menu>
      </t-aside>
      <t-layout>
        <t-header class="app-header">
          <div class="header-left">
            <span class="page-title">{{ pageTitle }}</span>
          </div>
          <div class="header-right">
            <t-avatar size="small">用户</t-avatar>
          </div>
        </t-header>
        <t-content class="app-content">
          <router-view />
        </t-content>
      </t-layout>
    </t-layout>
  </t-config-provider>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const globalConfig = {
  classPrefix: 't'
}

const activeMenu = computed(() => {
  const path = route.path.split('/')[1]
  return path || 'dashboard'
})

const pageTitle = computed(() => {
  const titles: Record<string, string> = {
    dashboard: '仪表盘',
    chat: 'AI 对话',
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
    gap: 16px;
  }
}

.app-content {
  padding: 24px;
  overflow: auto;
}
</style>
