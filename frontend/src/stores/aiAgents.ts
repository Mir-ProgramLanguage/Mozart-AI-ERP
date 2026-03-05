import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getAIAgents, createAIAgent, updateAIAgent, deleteAIAgent } from '@/api'
import type { AIAgent, CreateAIAgentRequest } from '@/api'

export const useAIAgentsStore = defineStore('aiAgents', () => {
  const agents = ref<AIAgent[]>([])
  const loading = ref(false)

  const fetchAgents = async () => {
    loading.value = true
    try {
      agents.value = await getAIAgents()
    } catch (error) {
      console.error('获取AI员工列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const create = async (data: CreateAIAgentRequest) => {
    const agent = await createAIAgent(data)
    agents.value.push(agent)
    return agent
  }

  const update = async (id: string, data: Partial<CreateAIAgentRequest>) => {
    const agent = await updateAIAgent(id, data)
    const index = agents.value.findIndex(a => a.id === id)
    if (index !== -1) {
      agents.value[index] = agent
    }
    return agent
  }

  const remove = async (id: string) => {
    await deleteAIAgent(id)
    agents.value = agents.value.filter(a => a.id !== id)
  }

  return {
    agents,
    loading,
    fetchAgents,
    create,
    update,
    remove
  }
})
