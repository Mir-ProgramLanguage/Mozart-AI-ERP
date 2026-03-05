<template>
  <div class="contributions-page">
    <!-- 概览统计 -->
    <t-row :gutter="24" style="margin-bottom: 24px;">
      <t-col :span="8">
        <t-card class="stat-card" :bordered="false">
          <div class="stat-value">{{ stats.totalValue }}</div>
          <div class="stat-label">总贡献值</div>
          <div class="stat-trend up">
            <t-icon name="arrow-up" />
            +12.5%
          </div>
        </t-card>
      </t-col>
      <t-col :span="8">
        <t-card class="stat-card" :bordered="false">
          <div class="stat-value">{{ stats.pendingValue }}</div>
          <div class="stat-label">待验证</div>
        </t-card>
      </t-col>
      <t-col :span="8">
        <t-card class="stat-card" :bordered="false">
          <div class="stat-value">{{ stats.verifiedValue }}</div>
          <div class="stat-label">已验证</div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 贡献记录列表 -->
    <t-card title="贡献记录" :bordered="false">
      <template #actions>
        <t-select v-model="filterStatus" style="width: 120px" placeholder="筛选状态">
          <t-option value="all" label="全部" />
          <t-option value="pending" label="待验证" />
          <t-option value="verified" label="已验证" />
          <t-option value="rejected" label="已拒绝" />
        </t-select>
      </template>

      <t-table
        :data="filteredContributions"
        :columns="columns"
        row-key="id"
        :pagination="{ pageSize: 10 }"
        hover
      >
        <template #status="{ row }">
          <t-tag
            :theme="statusTheme[row.status]"
            size="small"
          >
            {{ statusText[row.status] }}
          </t-tag>
        </template>
        <template #value="{ row }">
          <span class="value-cell">
            {{ row.actual_value || row.estimated_value }}
            <t-icon v-if="row.actual_value" name="check-circle" style="color: #52c41a; margin-left: 4px;" />
          </span>
        </template>
      </t-table>
    </t-card>

    <!-- 贡献类型分布 -->
    <t-row :gutter="24" style="margin-top: 24px;">
      <t-col :span="12">
        <t-card title="贡献类型分布" :bordered="false">
          <div ref="pieChartRef" style="height: 300px;"></div>
        </t-card>
      </t-col>
      <t-col :span="12">
        <t-card title="贡献趋势" :bordered="false">
          <div ref="lineChartRef" style="height: 300px;"></div>
        </t-card>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'

const filterStatus = ref('all')

const stats = ref({
  totalValue: '15,230',
  pendingValue: '2,100',
  verifiedValue: '13,130'
})

const contributions = ref([
  {
    id: '1',
    type: '采购节省',
    content: '发现土豆供应商，节省30%',
    estimated_value: 90,
    actual_value: 85,
    status: 'verified',
    created_at: '2026-03-06'
  },
  {
    id: '2',
    type: '销售机会',
    content: '介绍新客户王先生',
    estimated_value: 500,
    actual_value: null,
    status: 'pending',
    created_at: '2026-03-05'
  },
  {
    id: '3',
    type: '人才推荐',
    content: '推荐张三入职开发岗位',
    estimated_value: 5000,
    actual_value: 5000,
    status: 'verified',
    created_at: '2026-03-04'
  }
])

const statusTheme: Record<string, string> = {
  pending: 'warning',
  verified: 'success',
  rejected: 'danger'
}

const statusText: Record<string, string> = {
  pending: '待验证',
  verified: '已验证',
  rejected: '已拒绝'
}

const columns = [
  { colKey: 'type', title: '类型', width: 120 },
  { colKey: 'content', title: '内容', ellipsis: true },
  { colKey: 'value', title: '价值', width: 120, cell: 'value' },
  { colKey: 'status', title: '状态', width: 100, cell: 'status' },
  { colKey: 'created_at', title: '时间', width: 120 }
]

const filteredContributions = computed(() => {
  if (filterStatus.value === 'all') return contributions.value
  return contributions.value.filter(c => c.status === filterStatus.value)
})

const pieChartRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()

onMounted(() => {
  // 饼图
  if (pieChartRef.value) {
    const chart = echarts.init(pieChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data: [
          { value: 5000, name: '采购节省', itemStyle: { color: '#1890ff' } },
          { value: 4500, name: '销售贡献', itemStyle: { color: '#52c41a' } },
          { value: 3000, name: '人才推荐', itemStyle: { color: '#fa8c16' } },
          { value: 2000, name: '知识分享', itemStyle: { color: '#722ed1' } },
          { value: 730, name: '其他', itemStyle: { color: '#999' } }
        ]
      }]
    })
  }

  // 折线图
  if (lineChartRef.value) {
    const chart = echarts.init(lineChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: { type: 'value' },
      series: [{
        data: [1500, 2300, 1800, 2500, 3200, 2100, 1800],
        type: 'line',
        smooth: true,
        areaStyle: { color: 'rgba(24, 144, 255, 0.1)' },
        lineStyle: { color: '#1890ff', width: 3 },
        itemStyle: { color: '#1890ff' }
      }]
    })
  }
})
</script>

<style lang="scss" scoped>
.contributions-page {
  .stat-card {
    text-align: center;
    padding: 24px;

    .stat-value {
      font-size: 32px;
      font-weight: 600;
      color: #333;
    }

    .stat-label {
      font-size: 14px;
      color: #666;
      margin-top: 8px;
    }

    .stat-trend {
      margin-top: 12px;
      font-size: 14px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;

      &.up {
        color: #52c41a;
      }
      &.down {
        color: #ff4d4f;
      }
    }
  }

  .value-cell {
    font-weight: 500;
    color: #1890ff;
  }
}
</style>
