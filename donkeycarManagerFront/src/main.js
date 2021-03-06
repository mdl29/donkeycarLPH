// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'
import Vuesax from 'vuesax'
import 'vuesax/dist/vuesax.css'
import VueInsProgressBar from 'vue-ins-progress-bar'

const options = {
  position: 'fixed',
  show: true,
  height: '4px'
}

Vue.use(Vuesax, {
  // options here
})

Vue.use(VueInsProgressBar, options)

Vue.config.productionTip = false

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
