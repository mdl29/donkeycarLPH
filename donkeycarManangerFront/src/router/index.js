import Vue from 'vue'
import Router from 'vue-router'
import home from '@/components/home'
import register from '@/components/register'
import waitingBoard from '@/components/waitingBoard'
import dashboard from '@/components/dashboard'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'home',
      component: home
    },
    {
      path: '/register',
      name: 'register',
      component: register
    },
    {
      path: '/waitingBoard',
      name: 'waiting board',
      component: waitingBoard
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: dashboard
    }
  ]
})
