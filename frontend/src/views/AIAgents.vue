<template>
  <div class="ai-agents-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <t-button theme="primary" @click="showCreateDialog = true">
        <template #icon><t-icon name="add" /></template>
        创建 AI 员工
      </t-button>
    </div>

    <!-- AI 员工列表 -->
    <t-row :gutter="[24, 24]">
      <t-col :span="6" v-for="agent in aiAgentsStore.agents" :key="agent.id">
        <t-card class="agent-card" :bordered="false" hover-shadow>
          <div class="agent-avatar">
            {{ getAgentEmoji(agent) }}
          </div>
          <div class="agent-name">{{ agent.display_name }}</div>
          <div class="agent-status">
            <t-tag :theme="agent.is_active ? 'success' : 'default'" size="small">
              {{ agent.is_active ? '活跃' : '停用' }}
            </t-tag>
          </div>
          <div class="agent-capabilities">
            <t-tag
              v-for="(score, cap) in agent.capabilities"
              :key="cap"
              size="small"
              variant="outline"
              class="capability-tag"
            >
              {{ cap }}: {{ (score * 100).toFixed(0) }}%
            </t-tag>
          </div>
          <div class="agent-actions">
            <t-button size="small" variant="text" @click="editAgent(agent)">
              编辑
            </t-button>
            <t-button size="small" variant="text" theme="danger" @click="confirmDelete(agent)">
              删除
            </t-button>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 创建/编辑对话框 -->
    <t-dialog
      v-model:visible="showCreateDialog"
      :header="editingAgent ? '编辑 AI 员工' : '创建 AI 员工'"
      width="500px"
      @confirm="handleSave"
      @close="resetForm"
    >
      <t-form :data="formData" :rules="formRules" ref="formRef">
        <t-form-item label="名称" name="display_name">
          <t-input v-model="formData.display_name" placeholder="请输入AI员工名称" />
        </t-form-item>
        <t-form-item label="能力配置">
          <div class="capabilities-editor">
            <div v-for="(score, cap) in formData.capabilities" :key="cap" class="capability-item">
              <t-input v-model="formData.capabilities[cap]" style="flex: 1" />
              <t-slider v-model="formData.capabilities[cap]" :max="1" :step="0.1" style="width: 150px" />
              <t-button variant="text" theme="danger" @click="removeCapability(cap)">
                <t-icon name="close" />
              </t-button>
            </div>
            <t-button variant="dashed" block @click="addCapability">
              <t-icon name="add" /> 添加能力
            </t-button>
          </div>
        </t-form-item>
        <t-form-item label="模型">
          <t-select v-model="formData.ai_config.model">
            <t-option value="deepseek-chat" label="DeepSeek Chat" />
            <t-option value="deepseek-coder" label="DeepSeek Coder" />
            <t-option value="gpt-4" label="GPT-4" />
          </t-select>
        </t-form-item>
        <t-form-item label="系统提示">
          <t-textarea
            v-model="formData.ai_config.system_prompt"
            placeholder="定义AI员工的角色和行为"
            :autosize="{ minRows: 3, maxRows: 6 }"
          />
        </t-form-item>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAIAgentsStore } from '@/stores/aiAgents'
import { MessagePlugin, DialogPlugin } from 'tdesign-vue-next'
import type { AIAgent, CreateAIAgentRequest } from '@/api'

const aiAgentsStore = useAIAgentsStore()
const showCreateDialog = ref(false)
const editingAgent = ref<AIAgent | null>(null)
const formRef = ref()

const formData = reactive<CreateAIAgentRequest>({
  display_name: '',
  capabilities: {},
  ai_config: {
    model: 'deepseek-chat',
    temperature: 0.7,
    system_prompt: ''
  }
})

const formRules = {
  display_name: [{ required: true, message: '请输入名称' }]
}

const getAgentEmoji = (agent: AIAgent) => {
  const emojis = ['🤖', '🧠', '💡', '🎯', '📊', '💻', '📝', '🔍']
  const index = parseInt(agent.id.replace(/\D/g, '').slice(-1) || '0')
  return emojis[index % emojis.length]
}

const resetForm = () => {
  editingAgent.value = null
  formData.display_name = ''
  formData.capabilities = {}
  formData.ai_config = {
    model: 'deepseek-chat',
    temperature: 0.7,
    system_prompt: ''
  }
}

const addCapability = () => {
  const name = prompt('能力名称:')
  if (name && !formData.capabilities[name]) {
    formData.capabilities[name] = 0.8
  }
}

const removeCapability = (cap: string) => {
  delete formData.capabilities[cap]
}

const editAgent = (agent: AIAgent) => {
  editingAgent.value = agent
  formData.display_name = agent.display_name
  formData.capabilities = { ...agent.capabilities }
  formData.ai_config = { ...agent.ai_config }
  showCreateDialog.value = true
}

const handleSave = async () => {
  const valid = await formRef.value?.validate()
  if (valid !== true) return

  try {
    if (editingAgent.value) {
      await aiAgentsStore.update(editingAgent.value.id, formData)
      MessagePlugin.success('更新成功')
    } else {
      await aiAgentsStore.create(formData)
      MessagePlugin.success('创建成功')
    }
    showCreateDialog.value = false
    resetForm()
  } catch (error) {
    MessagePlugin.error('操作失败')
  }
}

const confirmDelete = (agent: AIAgent) => {
  const dialog = DialogPlugin.confirm({
    header: '确认删除',
    body: `确定要删除 AI 员工 "${agent.display_name}" 吗？`,
    onConfirm: async () => {
      try {
        await aiAgentsStore.remove(agent.id)
        MessagePlugin.success('删除成功')
        dialog.hide()
      } catch (error) {
        MessagePlugin.error('删除失败')
      }
    }
  })
}

onMounted(() => {
  aiAgentsStore.fetchAgents()
})
</script>

<style lang="scss" scoped>
.ai-agents-page {
  .page-header {
    margin-bottom: 24px;
    display: flex;
    justify-content: flex-end;
  }

  .agent-card {
    text-align: center;
    padding: 24px;

    .agent-avatar {
      width: 64px;
      height: 64px;
      margin: 0 auto 12px;
      font-size: 48px;
    }

    .agent-name {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 8px;
    }

    .agent-status {
      margin-bottom: 12px;
    }

    .agent-capabilities {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: center;
      margin-bottom: 16px;
      min-height: 28px;
    }

    .agent-actions {
      display: flex;
      justify-content: center;
      gap: 8px;
    }
  }

  .capabilities-editor {
    .capability-item {
      display: flex;
      gap: 8px;
      align-items: center;
      margin-bottom: 8px;
    }
  }
}
</style>
