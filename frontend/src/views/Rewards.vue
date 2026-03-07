<template>
  <div class="rewards-page">
    <!-- 回报概览 -->
    <t-row :gutter="24">
      <t-col :span="8">
        <t-card class="reward-card main" :bordered="false">
          <div class="reward-icon">💰</div>
          <div class="reward-info">
            <div class="reward-value">¥{{ rewards.available }}</div>
            <div class="reward-label">可兑现回报</div>
          </div>
          <t-button theme="primary" block @click="showRedeemDialog = true">
            立即兑现
          </t-button>
        </t-card>
      </t-col>
      <t-col :span="8">
        <t-card class="reward-card" :bordered="false">
          <div class="reward-icon">📊</div>
          <div class="reward-info">
            <div class="reward-value">{{ rewards.total }}</div>
            <div class="reward-label">累计回报</div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="8">
        <t-card class="reward-card" :bordered="false">
          <div class="reward-icon">🎯</div>
          <div class="reward-info">
            <div class="reward-value">{{ rewards.points }}</div>
            <div class="reward-label">技能点</div>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 回报历史 -->
    <t-card title="回报记录" :bordered="false" style="margin-top: 24px;">
      <template #actions>
        <t-dropdown :options="exportOptions" @click="handleExport">
          <t-button variant="outline">
            <template #icon><t-icon name="download" /></template>
            导出
          </t-button>
        </t-dropdown>
      </template>
      <t-tabs v-model="activeTab">
        <t-tab-panel value="all" label="全部">
          <RewardList :rewards="allRewards" />
        </t-tab-panel>
        <t-tab-panel value="pending" label="待领取">
          <RewardList :rewards="pendingRewards" />
        </t-tab-panel>
        <t-tab-panel value="claimed" label="已领取">
          <RewardList :rewards="claimedRewards" />
        </t-tab-panel>
      </t-tabs>
    </t-card>

    <!-- 兑现对话框 -->
    <t-dialog
      v-model:visible="showRedeemDialog"
      header="兑现回报"
      width="400px"
      @confirm="handleRedeem"
    >
      <div class="redeem-form">
        <div class="current-balance">
          当前可兑现：<span class="amount">¥{{ rewards.available }}</span>
        </div>
        <t-form :data="redeemForm" ref="redeemFormRef">
          <t-form-item label="兑现金额" name="amount">
            <t-input-number
              v-model="redeemForm.amount"
              :min="10"
              :max="parseFloat(rewards.available)"
              :step="10"
              style="width: 100%"
            />
          </t-form-item>
          <t-form-item label="兑现方式" name="type">
            <t-radio-group v-model="redeemForm.type">
              <t-radio value="alipay">支付宝</t-radio>
              <t-radio value="wechat">微信</t-radio>
              <t-radio value="bank">银行卡</t-radio>
            </t-radio-group>
          </t-form-item>
        </t-form>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { exportRewards } from '@/api'

// 导出选项
const exportOptions = [
  { content: '导出为 CSV', value: 'csv' },
  { content: '导出为 Excel', value: 'excel' },
  { content: '导出为 JSON', value: 'json' }
]

const handleExport = (data: { value: string }) => {
  const format = data.value as 'csv' | 'excel' | 'json'
  exportRewards(format, { status: activeTab.value === 'all' ? undefined : activeTab.value })
  MessagePlugin.success('正在导出数据...')
}

interface Reward {
  id: string
  type: string
  amount: number
  source: string
  status: 'pending' | 'claimed'
  created_at: string
  claimed_at?: string
}

const RewardList = {
  props: ['rewards'],
  template: `
    <t-list :split="true">
      <t-list-item v-for="item in rewards" :key="item.id">
        <t-list-item-meta
          :title="item.source"
          :description="item.created_at"
        >
          <template #avatar>
            <t-avatar :style="{ backgroundColor: getTypeColor(item.type) }">
              {{ getTypeIcon(item.type) }}
            </t-avatar>
          </template>
        </t-list-item-meta>
        <template #action>
          <div class="reward-amount" :class="{ claimed: item.status === 'claimed' }">
            {{ item.type === 'skill_points' ? '+' + item.amount + ' 技能点' : '¥' + item.amount }}
          </div>
        </template>
      </t-list-item>
    </t-list>
  `,
  methods: {
    getTypeColor(type: string) {
      const colors: Record<string, string> = {
        cash_bonus: '#52c41a',
        profit_sharing: '#1890ff',
        skill_points: '#722ed1'
      }
      return colors[type] || '#999'
    },
    getTypeIcon(type: string) {
      const icons: Record<string, string> = {
        cash_bonus: '¥',
        profit_sharing: '📈',
        skill_points: '⭐'
      }
      return icons[type] || '?'
    }
  }
}

const rewards = ref({
  available: '500.00',
  total: '1,500',
  points: '15.0'
})

const activeTab = ref('all')

const allRewards = ref<Reward[]>([
  {
    id: '1',
    type: 'cash_bonus',
    amount: 100,
    source: '采购节省贡献',
    status: 'claimed',
    created_at: '2026-03-06',
    claimed_at: '2026-03-06'
  },
  {
    id: '2',
    type: 'profit_sharing',
    amount: 400,
    source: '销售贡献分红',
    status: 'pending',
    created_at: '2026-03-05'
  },
  {
    id: '3',
    type: 'skill_points',
    amount: 5.0,
    source: '知识分享贡献',
    status: 'claimed',
    created_at: '2026-03-04'
  }
])

const pendingRewards = computed(() => allRewards.value.filter(r => r.status === 'pending'))
const claimedRewards = computed(() => allRewards.value.filter(r => r.status === 'claimed'))

const showRedeemDialog = ref(false)
const redeemFormRef = ref()
const redeemForm = reactive({
  amount: 100,
  type: 'alipay'
})

const handleRedeem = async () => {
  if (redeemForm.amount < 10) {
    MessagePlugin.warning('最低兑现金额为10元')
    return
  }
  
  MessagePlugin.success(`已提交兑现申请，预计1-3个工作日到账`)
  showRedeemDialog.value = false
}
</script>

<style lang="scss" scoped>
.rewards-page {
  .reward-card {
    text-align: center;
    padding: 32px 24px;

    &.main {
      background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
      color: #fff;

      .reward-value {
        color: #fff;
      }
      .reward-label {
        color: rgba(255, 255, 255, 0.85);
      }
    }

    .reward-icon {
      font-size: 40px;
      margin-bottom: 16px;
    }

    .reward-value {
      font-size: 36px;
      font-weight: 600;
      color: #333;
    }

    .reward-label {
      font-size: 14px;
      color: #666;
      margin-top: 8px;
      margin-bottom: 24px;
    }
  }

  .redeem-form {
    .current-balance {
      text-align: center;
      margin-bottom: 24px;
      font-size: 16px;

      .amount {
        font-size: 24px;
        font-weight: 600;
        color: #1890ff;
      }
    }
  }

  :deep(.reward-amount) {
    font-size: 16px;
    font-weight: 500;
    color: #52c41a;

    &.claimed {
      color: #999;
    }
  }
}
</style>
