<template>
  <div class="tasks-page">
    <!-- 任务看板 -->
    <t-row :gutter="24">
      <!-- 待处理 -->
      <t-col :span="6">
        <div class="task-column">
          <div class="column-header pending">
            <t-icon name="time" />
            <span>待处理</span>
            <t-badge :count="pendingTasks.length" />
          </div>
          <div class="column-content">
            <t-card
              v-for="task in pendingTasks"
              :key="task.id"
              class="task-card"
              :bordered="false"
              hover-shadow
            >
              <div class="task-type">{{ task.type }}</div>
              <div class="task-desc">{{ task.description }}</div>
              <div class="task-meta">
                <span class="priority" :class="`p${task.priority}`">
                  P{{ task.priority }}
                </span>
                <span class="time">{{ formatTime(task.created_at) }}</span>
              </div>
              <div class="task-actions">
                <t-button size="small" theme="primary" @click="claimTask(task)">
                  领取任务
                </t-button>
              </div>
            </t-card>
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
            >
              <div class="task-type">{{ task.type }}</div>
              <div class="task-desc">{{ task.description }}</div>
              <div class="task-meta">
                <span class="priority" :class="`p${task.priority}`">
                  P{{ task.priority }}
                </span>
                <span class="time">{{ formatTime(task.created_at) }}</span>
              </div>
              <div class="task-actions">
                <t-button size="small" theme="success" @click="completeTask(task)">
                  完成任务
                </t-button>
              </div>
            </t-card>
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
              class="task-card"
              :bordered="false"
            >
              <div class="task-type">{{ task.type }}</div>
              <div class="task-desc">{{ task.description }}</div>
              <div class="task-meta">
                <span class="time">{{ formatTime(task.completed_at || task.created_at) }}</span>
              </div>
            </t-card>
          </div>
        </div>
      </t-col>

      <!-- 已取消 -->
      <t-col :span="6">
        <div class="task-column">
          <div class="column-header cancelled">
            <t-icon name="close-circle" />
            <span>已取消</span>
            <t-badge :count="cancelledTasks.length" />
          </div>
          <div class="column-content">
            <t-card
              v-for="task in cancelledTasks"
              :key="task.id"
              class="task-card"
              :bordered="false"
            >
              <div class="task-type">{{ task.type }}</div>
              <div class="task-desc">{{ task.description }}</div>
            </t-card>
          </div>
        </div>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { MessagePlugin } from 'tdesign-vue-next'
import type { Task } from '@/api'

// 模拟数据
const tasks = ref<Task[]>([
  {
    id: '1',
    type: 'verify',
    description: '验证供应商张三的真实性',
    status: 'pending',
    priority: 1,
    created_at: new Date().toISOString()
  },
  {
    id: '2',
    type: 'execute',
    description: '采购土豆100斤',
    status: 'in_progress',
    priority: 2,
    created_at: new Date().toISOString()
  },
  {
    id: '3',
    type: 'approve',
    description: '审批采购单 #12345',
    status: 'completed',
    priority: 1,
    created_at: new Date(Date.now() - 86400000).toISOString(),
    completed_at: new Date().toISOString()
  }
])

const pendingTasks = computed(() => tasks.value.filter(t => t.status === 'pending'))
const inProgressTasks = computed(() => tasks.value.filter(t => t.status === 'in_progress'))
const completedTasks = computed(() => tasks.value.filter(t => t.status === 'completed'))
const cancelledTasks = computed(() => tasks.value.filter(t => t.status === 'cancelled'))

const formatTime = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const claimTask = (task: Task) => {
  task.status = 'in_progress'
  MessagePlugin.success('任务已领取')
}

const completeTask = (task: Task) => {
  task.status = 'completed'
  task.completed_at = new Date().toISOString()
  MessagePlugin.success('任务已完成')
}
</script>

<style lang="scss" scoped>
.tasks-page {
  min-height: calc(100vh - 64px - 48px);

  .task-column {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 16px;
    height: calc(100vh - 64px - 48px - 48px);
    display: flex;
    flex-direction: column;

    .column-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px;
      margin-bottom: 16px;
      border-radius: 6px;
      font-weight: 500;

      &.pending {
        background: #fff7e6;
        color: #fa8c16;
      }
      &.in-progress {
        background: #e6f7ff;
        color: #1890ff;
      }
      &.completed {
        background: #f6ffed;
        color: #52c41a;
      }
      &.cancelled {
        background: #fff1f0;
        color: #ff4d4f;
      }
    }

    .column-content {
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
  }

  .task-card {
    padding: 16px;

    .task-type {
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
    }

    .task-desc {
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 8px;
    }

    .task-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;

      .priority {
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 4px;

        &.p1 {
          background: #ff4d4f;
          color: #fff;
        }
        &.p2 {
          background: #fa8c16;
          color: #fff;
        }
        &.p3 {
          background: #faad14;
          color: #fff;
        }
      }

      .time {
        font-size: 12px;
        color: #999;
      }
    }

    .task-actions {
      display: flex;
      gap: 8px;
    }
  }
}
</style>
