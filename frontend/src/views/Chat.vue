<template>
  <div class="chat-page">
    <div class="chat-container">
      <!-- 消息列表 -->
      <div class="messages" ref="messagesRef">
        <div class="welcome-message" v-if="chatStore.messages.length === 0">
          <div class="welcome-icon">🤖</div>
          <h2>欢迎使用 Mozart AI ERP</h2>
          <p>我是您的核心AI助手，可以帮您：</p>
          <div class="feature-cards">
            <div class="feature-card" @click="quickAction('record')">
              <span class="feature-icon">📝</span>
              <span class="feature-title">记录业务</span>
              <span class="feature-desc">采购、销售、支出...</span>
            </div>
            <div class="feature-card" @click="quickAction('query')">
              <span class="feature-icon">🔍</span>
              <span class="feature-title">查询数据</span>
              <span class="feature-desc">统计、报表、分析...</span>
            </div>
            <div class="feature-card" @click="quickAction('task')">
              <span class="feature-icon">📋</span>
              <span class="feature-title">任务管理</span>
              <span class="feature-desc">创建、分配、追踪...</span>
            </div>
            <div class="feature-card" @click="quickAction('ai')">
              <span class="feature-icon">🤖</span>
              <span class="feature-title">AI 协作</span>
              <span class="feature-desc">写文案、写代码...</span>
            </div>
          </div>
        </div>

        <div
          v-for="(msg, index) in chatStore.messages"
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? '👤' : '🤖' }}
          </div>
          <div class="message-content">
            <!-- 贡献信息卡片 -->
            <div v-if="msg.contribution" class="contribution-card">
              <div class="contribution-header">
                <t-icon name="chart-bar" />
                <span>贡献已识别</span>
              </div>
              <div class="contribution-body">
                <div class="contribution-type">{{ msg.contribution.type || '通用贡献' }}</div>
                <div class="contribution-value">
                  预估价值: <strong>+{{ msg.contribution.estimated_value }}</strong>
                </div>
              </div>
            </div>
            
            <!-- 任务信息卡片 -->
            <div v-if="msg.tasks && msg.tasks.length > 0" class="tasks-card">
              <div class="tasks-header">
                <t-icon name="task" />
                <span>已创建 {{ msg.tasks.length }} 个任务</span>
              </div>
            </div>

            <!-- 消息内容 -->
            <div class="message-text" v-html="formatMarkdown(msg.content)"></div>
            
            <!-- 意图标签 -->
            <div v-if="msg.intent" class="intent-tag">
              <t-tag theme="primary" variant="light">{{ msg.intent }}</t-tag>
            </div>
            
            <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
          </div>
        </div>

        <div v-if="chatStore.loading" class="message assistant">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="quick-actions">
          <t-button size="small" variant="outline" @click="insertTemplate('purchase')">
            📦 采购
          </t-button>
          <t-button size="small" variant="outline" @click="insertTemplate('sales')">
            💰 销售
          </t-button>
          <t-button size="small" variant="outline" @click="insertTemplate('query')">
            📊 查询
          </t-button>
          <t-button size="small" variant="outline" @click="insertTemplate('task')">
            📋 任务
          </t-button>
        </div>
        <div class="input-row">
          <t-textarea
            v-model="inputMessage"
            placeholder="输入您的消息... (Shift+Enter 换行，Enter 发送)"
            :autosize="{ minRows: 1, maxRows: 4 }"
            @keydown.enter.exact="handleEnter"
            :disabled="chatStore.loading"
          />
          <t-button
            theme="primary"
            @click="sendMessage"
            :loading="chatStore.loading"
            :disabled="!inputMessage.trim()"
          >
            <template #icon><t-icon name="send" /></template>
          </t-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { MessagePlugin } from 'tdesign-vue-next'

const chatStore = useChatStore()
const inputMessage = ref('')
const messagesRef = ref<HTMLElement | null>(null)

const formatTime = (date: Date) => {
  return new Date(date).toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatMarkdown = (text: string) => {
  if (!text) return ''
  // 简单的 Markdown 格式化
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

watch(() => chatStore.messages.length, scrollToBottom)

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

const sendMessage = async () => {
  const message = inputMessage.value.trim()
  if (!message || chatStore.loading) return

  inputMessage.value = ''
  
  try {
    await chatStore.sendMessage(message)
  } catch (error) {
    MessagePlugin.error('发送失败，请重试')
  }
}

const quickAction = (type: string) => {
  const templates: Record<string, string> = {
    record: '今天采购了',
    query: '本月采购总额是多少？',
    task: '创建一个任务：',
    ai: '请AI助手帮我'
  }
  inputMessage.value = templates[type] || ''
}

const insertTemplate = (type: string) => {
  const templates: Record<string, string> = {
    purchase: '今天采购了20斤土豆，35元一斤，供应商张三',
    sales: '今天销售了50份套餐，每份28元',
    query: '本月销售额是多少？',
    task: '创建任务：完成用户登录模块开发，优先级高'
  }
  inputMessage.value = templates[type] || ''
}
</script>

<style lang="scss" scoped>
.chat-page {
  height: calc(100vh - 64px - 48px);
  display: flex;
  flex-direction: column;

  .chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #fff;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;

    .welcome-message {
      text-align: center;
      padding: 40px 20px;
      color: #666;

      .welcome-icon {
        font-size: 64px;
        margin-bottom: 16px;
      }

      h2 {
        font-size: 24px;
        margin-bottom: 8px;
        color: #333;
      }

      .feature-cards {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin-top: 24px;
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;

        .feature-card {
          padding: 20px;
          background: #f8f9fa;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s;
          text-align: left;

          &:hover {
            background: #e8f4ff;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          }

          .feature-icon {
            font-size: 28px;
            display: block;
            margin-bottom: 8px;
          }

          .feature-title {
            font-size: 14px;
            font-weight: 600;
            color: #333;
            display: block;
          }

          .feature-desc {
            font-size: 12px;
            color: #999;
            display: block;
            margin-top: 4px;
          }
        }
      }
    }

    .message {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;

      &.user {
        flex-direction: row-reverse;

        .message-content {
          align-items: flex-end;
        }

        .message-text {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #fff;
        }
      }

      .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
      }

      .message-content {
        display: flex;
        flex-direction: column;
        max-width: 70%;

        .contribution-card, .tasks-card {
          margin-bottom: 8px;
          padding: 12px;
          border-radius: 8px;
          background: #f0f9ff;
          border: 1px solid #bae7ff;

          .contribution-header, .tasks-header {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12px;
            color: #1890ff;
            margin-bottom: 8px;
          }

          .contribution-body {
            display: flex;
            justify-content: space-between;
            align-items: center;

            .contribution-type {
              font-weight: 500;
            }

            .contribution-value strong {
              color: #52c41a;
              font-size: 16px;
            }
          }
        }

        .message-text {
          padding: 12px 16px;
          border-radius: 16px;
          background: #f5f5f5;
          line-height: 1.6;
          word-break: break-word;

          code {
            background: rgba(0, 0, 0, 0.1);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
          }
        }

        .intent-tag {
          margin-top: 4px;
        }

        .message-time {
          font-size: 12px;
          color: #999;
          margin-top: 4px;
        }
      }
    }

    .typing {
      display: flex;
      gap: 4px;
      padding: 12px 16px !important;

      span {
        width: 8px;
        height: 8px;
        background: #999;
        border-radius: 50%;
        animation: typing 1.4s infinite ease-in-out;

        &:nth-child(2) { animation-delay: 0.2s; }
        &:nth-child(3) { animation-delay: 0.4s; }
      }
    }

    @keyframes typing {
      0%, 60%, 100% { transform: translateY(0); }
      30% { transform: translateY(-10px); }
    }
  }

  .input-area {
    padding: 16px 24px;
    border-top: 1px solid #f0f0f0;
    background: #fafafa;

    .quick-actions {
      display: flex;
      gap: 8px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }

    .input-row {
      display: flex;
      gap: 12px;
      align-items: flex-end;

      :deep(.t-textarea) {
        flex: 1;
      }
    }
  }
}
</style>
