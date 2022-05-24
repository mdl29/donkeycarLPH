<template>
<div>
    <h1> Liste d'attente</h1>
    <div class="table-wrapper">
      <vs-table >
        <template #thead>
          <vs-tr>
            <vs-th>
              ordre de passage
            </vs-th>
            <vs-th>
              pseudonyme
            </vs-th>
            <vs-th>
              Attente
            </vs-th>
          </vs-tr>
        </template>
        <template #tbody>
          <vs-tr v-for="player in poolPlayers" :key="player.player_id" >
            <vs-td>
              {{ player.player_id }}
            </vs-td>
            <vs-td>
              {{ player.player_pseudo }}
            </vs-td>
            <vs-td>
             <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg>
            </vs-td>
          </vs-tr>
        </template>
      </vs-table>
    </div>
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
    this.fetchDrivingQueue()
  },
  methods: {
    async fetchPlayers () {
      this.poolPlayers = await srv.getAllplayers(0, 20)
    },
    async fetchDrivingQueue () {
      this.drivingWaitingQueue = await srv.getDrivingWaitingQueue(true, 0, 20)
    }
  }
}
</script>

<style>
.table-wrapper{
  text-align: left !important;
  padding: 20px;
}
</style>
