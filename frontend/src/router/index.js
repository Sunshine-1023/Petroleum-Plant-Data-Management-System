import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '@/utils/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录', public: true, layout: 'blank' },
  },
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { title: '首页' } },
  { path: '/dept-query', name: 'dept-query', component: () => import('@/views/DeptQueryView.vue'), meta: { title: '单位查询' } },
  { path: '/cost-update', name: 'cost-update', component: () => import('@/views/CostUpdateView.vue'), meta: { title: '成本更新' } },
  { path: '/view-query', name: 'view-query', component: () => import('@/views/ViewQueryView.vue'), meta: { title: '视图查询' } },
  { path: '/db-demo', name: 'db-demo', component: () => import('@/views/DbDemoView.vue'), meta: { title: '数据库技术演示' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const loggedIn = isLoggedIn()

  if (to.meta.public) {
    if (to.path === '/login' && loggedIn) {
      return { path: '/' }
    }
    return true
  }

  if (!loggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  return true
})

router.afterEach((to) => {
  document.title = `${to.meta.title || '首页'} - 采油厂成本管理系统`
})

export default router
