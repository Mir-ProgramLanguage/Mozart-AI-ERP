<template>
  <div class="dashboard">
    <t-row :gutter="24">
      <!-- 统计卡片 -->
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false">
          <div class="stat-icon" style="background: #e6f7ff;">
            <t-icon name="chart-bar" style="color: #1890ff;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalContributions }}</div>
            <div class="stat-label">总贡献值</div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false">
          <div class="stat-icon" style="background: #f6ffed;">
            <t-icon name="gift" style="color: #52c41a;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.totalRewards }}</div>
            <div class="stat-label">总回报</div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false">
          <div class="stat-icon" style="background: #fffbe6;">
            <t-icon name="task" style="color: #faad14;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.pendingTasks }}</div>
            <div class="stat-label">待处理任务</div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false">
          <div class="stat-icon" style="background: #fff1f0;">
            <t-icon name="robot" style="color: #ff4d4f;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.aiAgents }}</div>
            <div class="stat-label">AI 员工</div>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-row :gutter="24" style="margin-top: 24px;">
      <!-- 快捷操作 -->
      <t-col :span="12">
        <t-card title="快捷操作" :bordered="false">
          <div class="quick-actions">
            <t-button theme="primary" @click="goToChat">
              <template #icon><t-icon name="chat" /></template>
              与 AI 对话
            </t-button>
            <t-button theme="default" @click="goToAgents">
              <template #icon><t-icon name="robot" /></template>
              管理 AI 员工
            </t-button>
            <t-button theme="default" @click="goToTasks">
              <template #icon><t-icon name="task" /></template>
              查看任务
            </t-button>
          </div>
        </t-card>
      </t-col>

      <!-- 最近活动 -->
      <t-col :span="12">
        <t-card title="最近活动" :bordered="false">
          <t-list :split="true">
            <t-list-item v-for="activity in recentActivities" :key="activity.id">
              <t-list-item-meta :title="activity.title" :description="activity.time" />
            </t-list-item>
          </t-list>
        </t-card>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAIAgentsStore } from '@/stores/aiAgents'

const router = useRouter()
const aiAgentsStore = useAIAgentsStore()

const stats = ref({
  totalContributions: '0',
  totalRewards: '¥0',
  pendingTasks: 0,
  aiAgents: 0
})

const recentActivities = ref([
  { id: 1, title: '系统已启动', time: '刚刚' }
])

onMounted(async () => {
  await aiAgentsStore.fetchAgents()
  stats.value.aiAgents = aiAgentsStore.agents.length
})

const goToChat = () => router.push('/chat')
const goToAgents = () => router.push('/ai-agents')
const goToTasks = () => router.push('/tasks')
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;

    .stat-icon {
      width: 56px;
      height: 56px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      margin-right: 16px;
    }

    .stat-content {
      .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: #333;
      }
      .stat-label {
        font-size: 14px;
        color: #666;
        margin-top: 4px;
      }
    }
  }

  .quick-actions {
    display: flex;
    gap: 12px;
  }
}
</style>
