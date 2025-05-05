import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/PaperList.vue')
  },
  {
    path: '/config',
    name: 'config',
    component: () => import('../views/ConfigEditor.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router