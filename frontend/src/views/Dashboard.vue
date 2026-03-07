<template>
  <div class="dashboard">
    <t-row :gutter="24">
      <!-- 统计卡片 -->
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false" hover>
          <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
            <t-icon name="chart-bar" style="color: #fff;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.contributions.total }}</div>
            <div class="stat-label">总贡献值</div>
            <div class="stat-trend" v-if="stats.contributions.pending > 0">
              <t-icon name="time-filled" /> {{ stats.contributions.pending }} 待验证
            </div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false" hover>
          <div class="stat-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
            <t-icon name="money-circle" style="color: #fff;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ formatNumber(stats.rewards.total) }}</div>
            <div class="stat-label">总回报</div>
            <div class="stat-trend" v-if="stats.rewards.pending > 0">
              <t-icon name="time-filled" /> ¥{{ stats.rewards.pending }} 待发放
            </div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false" hover>
          <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <t-icon name="task" style="color: #fff;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.tasks.pending + stats.tasks.in_progress }}</div>
            <div class="stat-label">进行中任务</div>
            <div class="stat-trend">
              <t-icon name="check-circle" /> {{ stats.tasks.completed }} 已完成
            </div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="6">
        <t-card class="stat-card" :bordered="false" hover>
          <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <t-icon name="usergroup" style="color: #fff;" />
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ actors.length }}</div>
            <div class="stat-label">团队成员</div>
            <div class="stat-trend">
              {{ aiAgentsCount }} AI 员工
            </div>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-row :gutter="24" style="margin-top: 24px;">
      <!-- 快捷操作 -->
      <t-col :span="8">
        <t-card title="快捷操作" :bordered="false">
          <div class="quick-actions">
            <t-button theme="primary" size="large" block @click="goToChat">
              <template #icon><t-icon name="chat" /></template>
              开始对话
            </t-button>
            <t-button theme="success" size="large" block @click="showContributeDialog = true">
              <template #icon><t-icon name="add" /></template>
              提交贡献
            </t-button>
            <t-button theme="warning" size="large" block @click="goToTasks">
              <template #icon><t-icon name="task" /></template>
              查看任务
            </t-button>
          </div>
        </t-card>
      </t-col>

      <!-- 最近活动 -->
      <t-col :span="8">
        <t-card title="最近活动" :bordered="false">
          <t-list :split="true" v-if="recentActivities.length > 0">
            <t-list-item v-for="activity in recentActivities" :key="activity.id">
              <t-list-item-meta>
                <template #avatar>
                  <span class="activity-icon">{{ activity.icon }}</span>
                </template>
                <template #title>{{ activity.title }}</template>
                <template #description>
                  <span class="activity-time">{{ activity.time }}</span>
                  <span v-if="activity.value" class="activity-value">+{{ activity.value }}</span>
                </template>
              </t-list-item-meta>
            </t-list-item>
          </t-list>
          <t-empty v-else description="暂无活动记录" />
        </t-card>
      </t-col>

      <!-- 排行榜 -->
      <t-col :span="8">
        <t-card title="贡献排行榜" :bordered="false">
          <div class="leaderboard">
            <div 
              v-for="(item, index) in leaderboard" 
              :key="item.actor.id" 
              class="leaderboard-item"
            >
              <span class="rank" :class="`rank-${index + 1}`">{{ index + 1 }}</span>
              <span class="name">{{ item.actor.display_name }}</span>
              <span class="value">{{ item.value }}</span>
            </div>
          </div>
          <t-empty v-if="leaderboard.length === 0" description="暂无排行数据" />
        </t-card>
      </t-col>
    </t-row>

    <!-- 快捷贡献对话框 -->
    <t-dialog
      v-model:visible="showContributeDialog"
      header="快速提交贡献"
      :confirm-btn="{ content: '提交', theme: 'primary' }"
      @confirm="submitContribution"
    >
      <t-form :data="contributionForm" :rules="contributionRules" ref="formRef">
        <t-form-item label="贡献类型" name="type">
          <t-select v-model="contributionForm.type">
            <t-option value="purchase" label="采购" />
            <t-option value="sales" label="销售" />
            <t-option value="recruitment" label="招聘" />
            <t-option value="knowledge" label="知识分享" />
            <t-option value="other" label="其他" />
          </t-select>
        </t-form-item>
        <t-form-item label="内容描述" name="content">
          <t-textarea
            v-model="contributionForm.content"
            placeholder="例如：今天采购了20斤土豆，35元一斤，供应商张三"
            :autosize="{ minRows: 3 }"
          />
        </t-form-item>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { MessagePlugin } from 'tdesign-vue-next'
import { useChatStore } from '@/stores/chat'
import { getActors, getLeaderboard, getMyContributions, say } from '@/api'

const router = useRouter()
const chatStore = useChatStore()

const stats = computed(() => chatStore.stats)

const actors = ref<any[]>([])
const leaderboard = ref<any[]>([])
const recentActivities = ref<any[]>([])

const showContributeDialog = ref(false)
const contributionForm = ref({ type: 'other', content: '' })
const contributionRules = {
  type: [{ required: true, message: '请选择贡献类型' }],
  content: [{ required: true, message: '请输入内容描述' }]
}
const formRef = ref()

const aiAgentsCount = computed(() => 
  actors.value.filter(a => a.actor_type === 'ai_agent').length
)

const formatNumber = (num: number) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + 'w'
  return num.toFixed(0)
}

const formatTimeAgo = (dateStr: string) => {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

onMounted(async () => {
  try {
    // 并行获取数据
    const [actorsRes, leaderboardRes, contributionsRes] = await Promise.all([
      getActors({ limit: 100 }),
      getLeaderboard('contribution', 5),
      getMyContributions(),
      chatStore.fetchStats()
    ])
    
    actors.value = actorsRes.items || []
    leaderboard.value = leaderboardRes || []
    
    // 转换最近贡献为活动
    recentActivities.value = (contributionsRes || []).slice(0, 5).map((c: any) => ({
      id: c.id,
      icon: getTypeIcon(c.contribution_type),
      title: c.content?.slice(0, 30) || '贡献',
      time: formatTimeAgo(c.created_at),
      value: c.contribution_value
    }))
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
})

const getTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    purchase: '🛒',
    sales: '💰',
    recruitment: '👥',
    knowledge: '📚',
    other: '✨'
  }
  return icons[type] || '📝'
}

const goToChat = () => router.push('/chat')
const goToTasks = () => router.push('/tasks')

const submitContribution = async () => {
  const valid = await formRef.value?.validate()
  if (valid !== true) return
  
  try {
    await say({ content: contributionForm.value.content })
    MessagePlugin.success('贡献提交成功！')
    showContributeDialog.value = false
    contributionForm.value = { type: 'other', content: '' }
    chatStore.fetchStats()
  } catch (error: any) {
    MessagePlugin.error(error.message || '提交失败')
  }
}
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28px;
      margin-right: 16px;
    }

    .stat-content {
      flex: 1;
      
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #333;
      }
      
      .stat-label {
        font-size: 14px;
        color: #666;
        margin-top: 4px;
      }
      
      .stat-trend {
        font-size: 12px;
        color: #999;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .quick-actions {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .activity-icon {
    font-size: 24px;
  }
  
  .activity-time {
    font-size: 12px;
    color: #999;
  }
  
  .activity-value {
    font-size: 12px;
    color: #52c41a;
    margin-left: 8px;
    font-weight: 500;
  }

  .leaderboard {
    .leaderboard-item {
      display: flex;
      align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid #f0f0f0;
      
      &:last-child {
        border-bottom: none;
      }
      
      .rank {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #f0f0f0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;
        margin-right: 12px;
        
        &.rank-1 { background: #ffd700; color: #fff; }
        &.rank-2 { background: #c0c0c0; color: #fff; }
        &.rank-3 { background: #cd7f32; color: #fff; }
      }
      
      .name {
        flex: 1;
        font-size: 14px;
      }
      
      .value {
        font-size: 14px;
        font-weight: 600;
        color: #1890ff;
      }
    }
  }
}
</style>
