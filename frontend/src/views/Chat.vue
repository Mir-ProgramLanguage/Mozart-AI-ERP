<template>
  <div class="chat-page">
    <div class="chat-container">
      <!-- 消息列表 -->
      <div class="messages" ref="messagesRef">
        <div class="welcome-message" v-if="chatStore.messages.length === 0">
          <div class="welcome-icon">🤖</div>
          <h2>欢迎使用 AI ERP</h2>
          <p>我是您的核心AI助手，可以帮您：</p>
          <ul>
            <li>📝 记录业务事件</li>
            <li>🔍 查询数据信息</li>
            <li>🤝 分配任务给AI员工</li>
            <li>📊 分析业务数据</li>
          </ul>
          <p class="tip">试着说："今天采购了20斤土豆，35元一斤"</p>
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
            <div class="message-text">{{ msg.content }}</div>
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
          发送
        </t-button>
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
    border-radius: 8px;
    overflow: hidden;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 24px;

    .welcome-message {
      text-align: center;
      padding: 60px 20px;
      color: #666;

      .welcome-icon {
        font-size: 64px;
        margin-bottom: 16px;
      }

      h2 {
        font-size: 24px;
        margin-bottom: 16px;
        color: #333;
      }

      ul {
        list-style: none;
        padding: 0;
        margin: 16px 0;
        
        li {
          padding: 8px 0;
          font-size: 16px;
        }
      }

      .tip {
        background: #f0f5ff;
        padding: 12px 20px;
        border-radius: 8px;
        display: inline-block;
        color: #1890ff;
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
          background: #1890ff;
          color: #fff;
        }
      }

      .message-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #f0f0f0;
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

        .message-text {
          padding: 12px 16px;
          border-radius: 12px;
          background: #f0f0f0;
          line-height: 1.6;
          word-break: break-word;
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
    display: flex;
    gap: 12px;
    align-items: flex-end;

    :deep(.t-textarea) {
      flex: 1;
    }
  }
}
</style>
