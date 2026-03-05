export type UUID = string

export interface Actor {
  id: UUID
  display_name: string
  actor_type: 'human' | 'ai_agent' | 'external'
  user_id?: number
  capabilities: Record<string, number>
  ai_config?: Record<string, any>
  total_contributions?: number
  total_rewards?: number
  created_at: string
  updated_at: string
}

export interface Contribution {
  id: UUID
  actor_id: UUID
  contribution_type: string
  content: string
  estimated_value: number
  actual_value?: number
  status: 'pending' | 'verified' | 'rejected'
  created_at: string
  verified_at?: string
}

export interface Reward {
  id: UUID
  actor_id: UUID
  event_id: UUID
  reward_type: string
  amount: number
  status: 'pending' | 'claimed'
  created_at: string
  claimed_at?: string
}
