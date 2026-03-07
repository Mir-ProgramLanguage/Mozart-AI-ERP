<template>
  <div class="tasks-page">
    <!-- 顶部操作栏 -->
    <t-card :bordered="false" style="margin-bottom: 16px;">
      <t-space>
        <t-button theme="primary" @click="showCreateDialog = true">
          <template #icon><t-icon name="add" /></template>
          创建任务
        </t-button>
        <t-button theme="default" @click="fetchTasks">
          <template #icon><t-icon name="refresh" /></template>
          刷新
        </t-button>
        <t-radio-group v-model="viewMode" variant="default-filled">
          <t-radio-button value="board">看板</t-radio-button>
          <t-radio-button value="list">列表</t-radio-button>
        </t-radio-group>
      </t-space>
    </t-card>

    <!-- 看板视图 -->
    <template v-if="viewMode === 'board'">
      <t-row :gutter="16">
        <!-- 待分配 -->
        <t-col :span="6">
          <div class="task-column">
            <div class="column-header pending">
              <t-icon name="time" />
              <span>待分配</span>
              <t-badge :count="pendingTasks.length" />
            </div>
            <div class="column-content">
              <t-card
                v-for="task in pendingTasks"
                :key="task.id"
                class="task-card"
                :bordered="false"
                hover-shadow
                @click="showTaskDetail(task)"
              >
                <div class="task-title">{{ task.title }}</div>
                <div class="task-desc">{{ task.description?.slice(0, 50) }}...</div>
                <div class="task-meta">
                  <t-tag size="small" :theme="typeTheme[task.type]">{{ typeLabels[task.type] || task.type }}</t-tag>
                  <span class="priority" :class="`p${task.priority}`">P{{ task.priority }}</span>
                </div>
                <div class="task-actions">
                  <t-button size="small" theme="primary" variant="outline" @click.stop="claimTask(task)">
                    领取
                  </t-button>
                  <t-button size="small" theme="default" variant="outline" @click.stop="autoAssign(task)">
                    自动分配
                  </t-button>
                </div>
              </t-card>
              <t-empty v-if="pendingTasks.length === 0" description="暂无任务" size="small" />
            </div>
          </div>
        </t-col>

        <!-- 已分配 -->
        <t-col :span="6">
          <div class="task-column">
            <div class="column-header assigned">
              <t-icon name="user" />
              <span>已分配</span>
              <t-badge :count="assignedTasks.length" />
            </div>
            <div class="column-content">
              <t-card
                v-for="task in assignedTasks"
                :key="task.id"
                class="task-card"
                :bordered="false"
                hover-shadow
                @click="showTaskDetail(task)"
              >
                <div class="task-title">{{ task.title }}</div>
                <div class="task-desc">{{ task.description?.slice(0, 50) }}...</div>
                <div class="task-meta">
                  <t-tag size="small" :theme="typeTheme[task.type]">{{ typeLabels[task.type] || task.type }}</t-tag>
                  <span class="priority" :class="`p${task.priority}`">P{{ task.priority }}</span>
                </div>
                <div class="task-assignees" v-if="task.assigned_actors?.length">
                  <t-avatar-group size="small" :max="3">
                    <t-avatar v-for="actor in task.assigned_actors" :key="actor.id">
                      {{ actor.display_name?.charAt(0) }}
                    </t-avatar>
                  </t-avatar-group>
                </div>
                <div class="task-actions">
                  <t-button size="small" theme="success" variant="outline" @click.stop="startTask(task)">
                    开始
                  </t-button>
                </div>
              </t-card>
              <t-empty v-if="assignedTasks.length === 0" description="暂无任务" size="small" />
            </div>
          </div>
        </t-col>

        <!-- 进行中 -->
        <t-col :span="6">
          <div class="task-column">
            <div class="column-header in-progress">
              <t-icon name="loading" />
              <span>进行中</span>
              <t-badge :count="inProgressTasks.length" />
            </div>
            <div class="column-content">
              <t-card
                v-for="task in inProgressTasks"
                :key="task.id"
                class="task-card"
                :bordered="false"
                hover-shadow
                @click="showTaskDetail(task)"
              >
                <div class="task-title">{{ task.title }}</div>
                <div class="task-desc">{{ task.description?.slice(0, 50) }}...</div>
                <div class="task-meta">
                  <t-tag size="small" :theme="typeTheme[task.type]">{{ typeLabels[task.type] || task.type }}</t-tag>
                  <span class="priority" :class="`p${task.priority}`">P{{ task.priority }}</span>
                </div>
                <div class="task-assignees" v-if="task.assigned_actors?.length">
                  <t-avatar-group size="small" :max="3">
                    <t-avatar v-for="actor in task.assigned_actors" :key="actor.id">
                      {{ actor.display_name?.charAt(0) }}
                    </t-avatar>
                  </t-avatar-group>
                </div>
                <div class="task-actions">
                  <t-button size="small" theme="success" @click.stop="completeTask(task)">
                    完成
                  </t-button>
                </div>
              </t-card>
              <t-empty v-if="inProgressTasks.length === 0" description="暂无任务" size="small" />
            </div>
          </div>
        </t-col>

        <!-- 已完成 -->
        <t-col :span="6">
          <div class="task-column">
            <div class="column-header completed">
              <t-icon name="check-circle" />
              <span>已完成</span>
              <t-badge :count="completedTasks.length" />
            </div>
            <div class="column-content">
              <t-card
                v-for="task in completedTasks"
                :key="task.id"
                class="task-card completed"
                :bordered="false"
                @click="showTaskDetail(task)"
              >
                <div class="task-title">{{ task.title }}</div>
                <div class="task-desc">{{ task.description?.slice(0, 50) }}...</div>
                <div class="task-meta">
                  <t-tag size="small" :theme="typeTheme[task.type]">{{ typeLabels[task.type] || task.type }}</t-tag>
                  <span class="time">{{ formatTime(task.completed_at) }}</span>
                </div>
                <div class="task-value" v-if="task.contribution_value">
                  贡献值: +{{ task.contribution_value }}
                </div>
              </t-card>
              <t-empty v-if="completedTasks.length === 0" description="暂无任务" size="small" />
            </div>
          </div>
        </t-col>
      </t-row>
    </template>

    <!-- 列表视图 -->
    <template v-else>
      <t-card :bordered="false">
        <t-table
          :data="tasks"
          :columns="tableColumns"
          row-key="id"
          :loading="loading"
          :pagination="pagination"
          @page-change="onPageChange"
          hover
        >
          <template #type="{ row }">
            <t-tag size="small" :theme="typeTheme[row.type]">{{ typeLabels[row.type] || row.type }}</t-tag>
          </template>
          <template #status="{ row }">
            <t-tag :theme="statusTheme[row.status]" size="small">
              {{ statusText[row.status] }}
            </t-tag>
          </template>
          <template #op="{ row }">
            <t-space>
              <t-link v-if="row.status === 'pending'" theme="primary" @click="claimTask(row)">领取</t-link>
              <t-link v-if="row.status === 'assigned'" theme="primary" @click="startTask(row)">开始</t-link>
              <t-link v-if="row.status === 'in_progress'" theme="success" @click="completeTask(row)">完成</t-link>
            </t-space>
          </template>
        </t-table>
      </t-card>
    </template>

    <!-- 创建任务对话框 -->
    <t-dialog
      v-model:visible="showCreateDialog"
      header="创建任务"
      width="500px"
      :confirm-btn="{ content: '创建', theme: 'primary', loading: creating }"
      @confirm="handleCreateTask"
    >
      <t-form :data="createForm" :rules="createRules" ref="formRef">
        <t-form-item label="任务类型" name="type">
          <t-select v-model="createForm.type">
            <t-option value="verify" label="验证" />
            <t-option value="approve" label="审批" />
            <t-option value="execute" label="执行" />
            <t-option value="evaluate" label="评估" />
          </t-select>
        </t-form-item>
        <t-form-item label="任务标题" name="title">
          <t-input v-model="createForm.title" placeholder="输入任务标题" />
        </t-form-item>
        <t-form-item label="任务描述" name="description">
          <t-textarea v-model="createForm.description" :autosize="{ minRows: 3 }" />
        </t-form-item>
        <t-form-item label="优先级" name="priority">
          <t-radio-group v-model="createForm.priority">
            <t-radio :value="1">P1 紧急</t-radio>
            <t-radio :value="2">P2 重要</t-radio>
            <t-radio :value="3">P3 普通</t-radio>
          </t-radio-group>
        </t-form-item>
      </t-form>
    </t-dialog>

    <!-- 任务详情抽屉 -->
    <t-drawer v-model:visible="showDetailDrawer" :header="currentTask?.title" size="large">
      <div class="task-detail" v-if="currentTask">
        <t-descriptions :column="2">
          <t-descriptions-item label="类型">{{ typeLabels[currentTask.type] || currentTask.type }}</t-descriptions-item>
          <t-descriptions-item label="状态">
            <t-tag :theme="statusTheme[currentTask.status]">{{ statusText[currentTask.status] }}</t-tag>
          </t-descriptions-item>
          <t-descriptions-item label="优先级">P{{ currentTask.priority }}</t-descriptions-item>
          <t-descriptions-item label="创建时间">{{ formatTime(currentTask.created_at) }}</t-descriptions-item>
          <t-descriptions-item label="描述" :span="2">{{ currentTask.description }}</t-descriptions-item>
          <t-descriptions-item label="负责人" :span="2">
            <t-space v-if="currentTask.assigned_actors?.length">
              <t-tag v-for="actor in currentTask.assigned_actors" :key="actor.id">
                {{ actor.display_name }}
              </t-tag>
            </t-space>
            <span v-else>未分配</span>
          </t-descriptions-item>
        </t-descriptions>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import { getTasks, createTask, startTask as startTaskApi, completeTask as completeTaskApi, autoAssignTask as autoAssignApi } from '@/api'
import type { Task } from '@/api'

const loading = ref(false)
const creating = ref(false)
const viewMode = ref<'board' | 'list'>('board')
const tasks = ref<Task[]>([])
const showCreateDialog = ref(false)
const showDetailDrawer = ref(false)
const currentTask = ref<Task | null>(null)
const formRef = ref()

const pagination = ref({
  current: 1,
  pageSize: 20,
  total: 0,
  showJumper: true,
  pageSizeOptions: [10, 20, 50, 100]
})

const createForm = ref({
  type: 'execute',
  title: '',
  description: '',
  priority: 3
})

const createRules = {
  type: [{ required: true, message: '请选择任务类型' }],
  title: [{ required: true, message: '请输入任务标题' }],
  description: [{ required: true, message: '请输入任务描述' }]
}

const typeLabels: Record<string, string> = {
  verify: '验证',
  approve: '审批',
  execute: '执行',
  evaluate: '评估'
}

const typeTheme: Record<string, string> = {
  verify: 'primary',
  approve: 'warning',
  execute: 'success',
  evaluate: 'default'
}

const statusTheme: Record<string, string> = {
  pending: 'warning',
  assigned: 'default',
  in_progress: 'primary',
  completed: 'success',
  verified: 'success',
  cancelled: 'danger'
}

const statusText: Record<string, string> = {
  pending: '待分配',
  assigned: '已分配',
  in_progress: '进行中',
  completed: '已完成',
  verified: '已验证',
  cancelled: '已取消'
}

const tableColumns = [
  { colKey: 'type', title: '类型', width: 80, cell: 'type' },
  { colKey: 'title', title: '标题', ellipsis: true },
  { colKey: 'status', title: '状态', width: 100, cell: 'status' },
  { colKey: 'priority', title: '优先级', width: 80 },
  { colKey: 'created_at', title: '创建时间', width: 120,
    cell: (h: any, { row }: any) => formatTime(row.created_at) },
  { colKey: 'op', title: '操作', width: 120, cell: 'op' }
]

const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'pending'))
const assignedTasks = computed(() => tasks.value.filter(t => t.status === 'assigned'))
const inProgressTasks = computed(() => tasks.value.filter(t => t.status === 'in_progress'))
const completedTasks = computed(() => tasks.value.filter(t => ['completed', 'verified'].includes(t.status)))

const formatTime = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchTasks = async () => {
  loading.value = true
  try {
    const res = await getTasks({
      skip: (pagination.value.current - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    })
    tasks.value = res.items || []
    pagination.value.total = res.total || 0
  } catch (error) {
    console.error('Failed to fetch tasks:', error)
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
  fetchTasks()
}

const handleCreateTask = async () => {
  const valid = await formRef.value?.validate()
  if (valid !== true) return
  
  creating.value = true
  try {
    await createTask({
      type: createForm.value.type,
      title: createForm.value.title,
      description: createForm.value.description,
      priority: createForm.value.priority
    })
    MessagePlugin.success('任务创建成功！')
    showCreateDialog.value = false
    createForm.value = { type: 'execute', title: '', description: '', priority: 3 }
    fetchTasks()
  } catch (error: any) {
    MessagePlugin.error(error.message || '创建失败')
  } finally {
    creating.value = false
  }
}

const claimTask = async (task: Task) => {
  try {
    await startTaskApi(task.id)
    MessagePlugin.success('任务已开始')
    fetchTasks()
  } catch (error: any) {
    MessagePlugin.error(error.message || '操作失败')
  }
}

const autoAssign = async (task: Task) => {
  try {
    await autoAssignApi(task.id)
    MessagePlugin.success('已自动分配')
    fetchTasks()
  } catch (error: any) {
    MessagePlugin.error(error.message || '分配失败')
  }
}

const startTask = async (task: Task) => {
  try {
    await startTaskApi(task.id)
    MessagePlugin.success('任务已开始')
    fetchTasks()
  } catch (error: any) {
    MessagePlugin.error(error.message || '操作失败')
  }
}

const completeTask = async (task: Task) => {
  try {
    await completeTaskApi(task.id)
    MessagePlugin.success('任务已完成')
    fetchTasks()
  } catch (error: any) {
    MessagePlugin.error(error.message || '操作失败')
  }
}

const showTaskDetail = (task: Task) => {
  currentTask.value = task
  showDetailDrawer.value = true
}

onMounted(fetchTasks)
</script>

<style lang="scss" scoped>
.tasks-page {
  min-height: calc(100vh - 64px - 48px);

  .task-column {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 12px;
    height: calc(100vh - 64px - 48px - 80px);
    display: flex;
    flex-direction: column;

    .column-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 10px 12px;
      margin-bottom: 12px;
      border-radius: 6px;
      font-weight: 500;
      font-size: 14px;

      &.pending { background: #fff7e6; color: #fa8c16; }
      &.assigned { background: #f0f5ff; color: #2f54eb; }
      &.in-progress { background: #e6f7ff; color: #1890ff; }
      &.completed { background: #f6ffed; color: #52c41a; }
    }

    .column-content {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
  }

  .task-card {
    padding: 14px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      transform: translateY(-2px);
    }
    
    &.completed {
      opacity: 0.7;
    }

    .task-title {
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 6px;
      color: #333;
    }

    .task-desc {
      font-size: 12px;
      color: #666;
      margin-bottom: 10px;
    }

    .task-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;

      .priority {
        font-size: 11px;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 500;

        &.p1 { background: #ff4d4f; color: #fff; }
        &.p2 { background: #fa8c16; color: #fff; }
        &.p3 { background: #faad14; color: #fff; }
      }
      
      .time {
        font-size: 11px;
        color: #999;
      }
    }
    
    .task-assignees {
      margin-bottom: 10px;
    }

    .task-actions {
      display: flex;
      gap: 8px;
    }
    
    .task-value {
      font-size: 12px;
      color: #52c41a;
      font-weight: 500;
      margin-top: 8px;
    }
  }
}
</style>
