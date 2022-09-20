import { createRouter, createWebHashHistory } from 'vue-router'
import registerView from '../views/registerView.vue'

const routes = [
  {
    path: '/',
    name: 'registerView',
    component: registerView
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})
export default router
