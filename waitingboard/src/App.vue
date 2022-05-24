<template>
  <div id="app">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <router-view/>
  </div>
</template>
<script>

import DonkeycarManagerService from '@/js/service.js'

const ip = 'localhost'
const srv = new DonkeycarManagerService('http://' + ip + ':8000')

export default {
  data: () => ({
    poolPlayers: [],
    drivingWaitingQueue: [],
    cars: null
  }),
  mounted () {
    this.fetchPlayers()
  },
  methods: {
    async fetchPlayers () {
      this.poolPlayers = await srv.getAllplayers(0, 20)
    }
  }
}
</script>

<style>

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
.title-header{
  font-family: 'Merriweather Sans', sans-serif;
  font-size: 35px;
  font-weight: bold;
}
</style>
