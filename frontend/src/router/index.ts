import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue')
  },
  {
    path: '/ai-agents',
    name: 'AIAgents',
    component: () => import('@/views/AIAgents.vue')
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('@/views/Tasks.vue')
  },
  {
    path: '/contributions',
    name: 'Contributions',
    component: () => import('@/views/Contributions.vue')
  },
  {
    path: '/rewards',
    name: 'Rewards',
    component: () => import('@/views/Rewards.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
