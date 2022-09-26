import { createRouter, createWebHashHistory } from 'vue-router'
import registerView from '../views/registerView.vue'
import dashboardView from '../views/dashboardView.vue'
import clientView from '../views/clientView.vue'

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
  },
  {
    path: '/client',
    name: 'client',
    component: clientView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})
export default router
