import { createRouter, createWebHashHistory } from 'vue-router'
import registerView from '../views/registerView.vue'
import dashboardView from '../views/dashboardView.vue'

const routes = [
  {
    path: '/',
    name: 'registerView',
    component: registerView
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: dashboardView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})
export default router
