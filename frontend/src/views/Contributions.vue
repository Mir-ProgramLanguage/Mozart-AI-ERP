<template>
  <div class="contributions-page">
    <!-- 概览统计 -->
    <t-row :gutter="24" style="margin-bottom: 24px;">
      <t-col :span="8">
        <t-card class="stat-card gradient-blue" :bordered="false">
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总贡献值</div>
        </t-card>
      </t-col>
      <t-col :span="8">
        <t-card class="stat-card gradient-orange" :bordered="false">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待验证</div>
        </t-card>
      </t-col>
      <t-col :span="8">
        <t-card class="stat-card gradient-green" :bordered="false">
          <div class="stat-value">{{ stats.verified }}</div>
          <div class="stat-label">已验证</div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 贡献记录列表 -->
    <t-card title="贡献记录" :bordered="false">
      <template #actions>
        <t-space>
          <t-select v-model="filterStatus" style="width: 120px" placeholder="状态" clearable>
            <t-option value="" label="全部" />
            <t-option value="pending" label="待验证" />
            <t-option value="verified" label="已验证" />
            <t-option value="rejected" label="已拒绝" />
          </t-select>
          <t-dropdown :options="exportOptions" @click="handleExport">
            <t-button variant="outline">
              <template #icon><t-icon name="download" /></template>
              导出
            </t-button>
          </t-dropdown>
          <t-button theme="primary" @click="showCreateDialog = true">
            <template #icon><t-icon name="add" /></template>
            提交贡献
          </t-button>
        </t-space>
      </template>

      <t-table
        :data="filteredContributions"
        :columns="columns"
        row-key="id"
        :loading="loading"
        :pagination="pagination"
        @page-change="onPageChange"
        hover
      >
        <template #contribution_type="{ row }">
          <t-tag theme="primary" variant="light">
            {{ typeLabels[row.contribution_type] || row.contribution_type }}
          </t-tag>
        </template>
        <template #content="{ row }">
          <div class="content-cell">
            <span class="content-text">{{ row.content?.slice(0, 50) }}{{ row.content?.length > 50 ? '...' : '' }}</span>
            <t-tag v-if="row.risk_level && row.risk_level !== 'none'" 
                   :theme="row.risk_level === 'high' ? 'danger' : 'warning'" 
                   size="small">
              {{ row.risk_level }}风险
            </t-tag>
          </div>
        </template>
        <template #value="{ row }">
          <span class="value-cell">
            {{ row.actual_value || row.contribution_value }}
            <t-icon v-if="row.actual_value" name="check-circle" style="color: #52c41a; margin-left: 4px;" />
          </span>
        </template>
        <template #status="{ row }">
          <t-tag :theme="statusTheme[row.status]" size="small">
            {{ statusText[row.status] }}
          </t-tag>
        </template>
        <template #op="{ row }">
          <t-space v-if="row.status === 'pending'">
            <t-link theme="primary" @click="verifyContribution(row.id, true)">通过</t-link>
            <t-link theme="danger" @click="verifyContribution(row.id, false)">拒绝</t-link>
          </t-space>
          <t-link v-else theme="primary" @click="viewDetail(row)">详情</t-link>
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
        <t-card title="贡献趋势（近7天）" :bordered="false">
          <div ref="lineChartRef" style="height: 300px;"></div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 提交贡献对话框 -->
    <t-dialog
      v-model:visible="showCreateDialog"
      header="提交贡献"
      width="500px"
      :confirm-btn="{ content: '提交', theme: 'primary', loading: submitting }"
      @confirm="submitContribution"
    >
      <t-form :data="createForm" :rules="createRules" ref="formRef">
        <t-form-item label="贡献类型" name="contribution_type">
          <t-select v-model="createForm.contribution_type">
            <t-option value="purchase" label="采购" />
            <t-option value="sales" label="销售" />
            <t-option value="recruitment" label="招聘" />
            <t-option value="knowledge" label="知识分享" />
            <t-option value="other" label="其他" />
          </t-select>
        </t-form-item>
        <t-form-item label="内容描述" name="content">
          <t-textarea
            v-model="createForm.content"
            placeholder="例如：今天采购了20斤土豆，35元一斤，供应商张三"
            :autosize="{ minRows: 3 }"
          />
        </t-form-item>
        <t-form-item label="详细信息" name="details">
          <t-textarea
            v-model="createForm.detailsJson"
            placeholder="JSON 格式的详细信息（可选）"
            :autosize="{ minRows: 2 }"
          />
        </t-form-item>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { MessagePlugin } from 'tdesign-vue-next'
import { getContributions, createContribution, verifyContribution as verifyContributionApi, exportContributions } from '@/api'
import type { Contribution } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const filterStatus = ref('')
const showCreateDialog = ref(false)
const contributions = ref<Contribution[]>([])
const formRef = ref()

// 导出选项
const exportOptions = [
  { content: '导出为 CSV', value: 'csv' },
  { content: '导出为 Excel', value: 'excel' },
  { content: '导出为 JSON', value: 'json' }
]

const handleExport = (data: { value: string }) => {
  const format = data.value as 'csv' | 'excel' | 'json'
  exportContributions(format, { status: filterStatus.value || undefined })
  MessagePlugin.success('正在导出数据...')
}

const stats = ref({ total: 0, pending: 0, verified: 0 })
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showJumper: true,
  pageSizeOptions: [10, 20, 50, 100]
})

const createForm = ref({
  contribution_type: 'other',
  content: '',
  detailsJson: ''
})

const createRules = {
  contribution_type: [{ required: true, message: '请选择贡献类型' }],
  content: [{ required: true, message: '请输入内容描述' }]
}

const typeLabels: Record<string, string> = {
  purchase: '采购',
  sales: '销售',
  recruitment: '招聘',
  knowledge: '知识分享',
  other: '其他'
}

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
  { colKey: 'contribution_type', title: '类型', width: 100, cell: 'contribution_type' },
  { colKey: 'content', title: '内容', ellipsis: true, cell: 'content' },
  { colKey: 'value', title: '价值', width: 100, cell: 'value' },
  { colKey: 'confidence', title: '置信度', width: 80, 
    cell: (h: any, { row }: any) => `${Math.round(row.confidence * 100)}%` },
  { colKey: 'status', title: '状态', width: 90, cell: 'status' },
  { colKey: 'created_at', title: '时间', width: 100,
    cell: (h: any, { row }: any) => new Date(row.created_at).toLocaleDateString() },
  { colKey: 'op', title: '操作', width: 120, cell: 'op' }
]

const filteredContributions = computed(() => {
  if (!filterStatus.value) return contributions.value
  return contributions.value.filter(c => c.status === filterStatus.value)
})

const pieChartRef = ref<HTMLElement>()
const lineChartRef = ref<HTMLElement>()

const fetchContributions = async () => {
  loading.value = true
  try {
    const res = await getContributions({
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    contributions.value = res.items || []
    pagination.value.total = res.total || 0
    
    // 计算统计
    stats.value = {
      total: contributions.value.reduce((sum, c) => sum + (c.actual_value || c.contribution_value), 0),
      pending: contributions.value.filter(c => c.status === 'pending').reduce((sum, c) => sum + c.contribution_value, 0),
      verified: contributions.value.filter(c => c.status === 'verified').reduce((sum, c) => sum + (c.actual_value || c.contribution_value), 0)
    }
  } catch (error) {
    console.error('Failed to fetch contributions:', error)
  } finally {
    loading.value = false
  }
}

const onPageChange = (pageInfo: any) => {
  // TDesign分页事件参数格式：{ current: number, pageSize: number }
  if (typeof pageInfo === 'object' && pageInfo !== null) {
    pagination.value.current = pageInfo.current || pageInfo
    pagination.value.pageSize = pageInfo.pageSize || pagination.value.pageSize
  } else if (typeof pageInfo === 'number') {
    pagination.value.current = pageInfo
  }
  fetchContributions()
}

const submitContribution = async () => {
  const valid = await formRef.value?.validate()
  if (valid !== true) return
  
  submitting.value = true
  try {
    let details = {}
    if (createForm.value.detailsJson) {
      try {
        details = JSON.parse(createForm.value.detailsJson)
      } catch (e) {
        MessagePlugin.warning('详细信息 JSON 格式不正确，已忽略')
      }
    }
    
    await createContribution({
      contribution_type: createForm.value.contribution_type,
      content: createForm.value.content,
      details
    })
    
    MessagePlugin.success('贡献提交成功！')
    showCreateDialog.value = false
    createForm.value = { contribution_type: 'other', content: '', detailsJson: '' }
    fetchContributions()
  } catch (error: any) {
    MessagePlugin.error(error.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const verifyContribution = async (id: string, approved: boolean) => {
  try {
    await verifyContributionApi(id, { approved })
    MessagePlugin.success(approved ? '已通过验证' : '已拒绝')
    fetchContributions()
  } catch (error: any) {
    MessagePlugin.error(error.message || '操作失败')
  }
}

const viewDetail = (row: Contribution) => {
  MessagePlugin.info(`贡献详情: ${row.content}`)
}

onMounted(async () => {
  await fetchContributions()
  
  // 饼图
  if (pieChartRef.value) {
    const chart = echarts.init(pieChartRef.value)
    const typeStats: Record<string, number> = {}
    contributions.value.forEach(c => {
      const type = typeLabels[c.contribution_type] || c.contribution_type
      typeStats[type] = (typeStats[type] || 0) + (c.actual_value || c.contribution_value)
    })
    
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
        data: Object.entries(typeStats).map(([name, value]) => ({ name, value }))
      }]
    })
  }

  // 折线图
  if (lineChartRef.value) {
    const chart = echarts.init(lineChartRef.value)
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: days },
      yAxis: { type: 'value' },
      series: [{
        data: [150, 230, 180, 250, 320, 210, 180],
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
    color: #fff;

    .stat-value {
      font-size: 36px;
      font-weight: 700;
    }

    .stat-label {
      font-size: 14px;
      opacity: 0.9;
      margin-top: 8px;
    }
    
    &.gradient-blue {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    &.gradient-orange {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    &.gradient-green {
      background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
  }

  .content-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .content-text {
      flex: 1;
    }
  }

  .value-cell {
    font-weight: 600;
    color: #1890ff;
  }
}
</style>
