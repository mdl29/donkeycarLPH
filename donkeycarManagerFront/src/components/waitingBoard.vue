<template>
<div>
    <h1> Liste d'attente</h1>
    <div class="table-wrapper" v-if=" drivingWaitingQueue !== undefined ">
      <vs-table>
        <template #thead>
          <vs-tr>
            <vs-th>
              Ordre de passage
            </vs-th>
            <vs-th>
              Pseudonyme
            </vs-th>
            <vs-th>
              Attente Estimé
            </vs-th>
            <vs-th>
              Création
            </vs-th>
          </vs-tr>
        </template>
        <template #tbody>
          <vs-tr v-for="(DrivingContent,i) in drivingWaitingQueue" v-bind:key="DrivingContent.rank">
            <vs-td>
              {{ i + 1 }}
            </vs-td>
            <vs-td>
              {{ DrivingContent.player.player_pseudo }}
            </vs-td>
            <vs-td v-if="i<2">15 min <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg></vs-td>
            <vs-td v-if="i>=2 && i<4">30 min <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg></vs-td>
            <vs-td v-if="i>=4&& i<6">45 min <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg></vs-td>
            <vs-td v-if="i>=6&& i<8">1 heure <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg></vs-td>
            <vs-td v-if="i>=8">Plus de 1 heure <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg></vs-td>
            <vs-td>
              Créé {{ timestamps[i] }}
            </vs-td>
          </vs-tr>
        </template>
      </vs-table>
    </div>
</div>
</template>
<script>

import DonkeycarManagerService from '@/js/service.js'

const { io } = require('socket.io-client')
const moment = require('moment')

moment.locale('fr')

const ip = DonkeycarManagerService.ip
const srv = new DonkeycarManagerService('http://' + ip + ':8000')
var socket = io.connect('http://' + ip + ':8000', { path: '/ws/socket.io' })

function getISOFromNow (iso) {
  const date = new Date(iso)
  const timestamp = date.getTime()
  const fromNow = moment(timestamp).fromNow()
  return fromNow
}

export default {
  data: () => ({
    drivingWaitingQueue: [],
    timestamps: [],
    interval: 0
  }),
  mounted () {
    this.fetchDrivingQueue()
  },
  created () {
    const that = this
    socket.on('jobs.all.updated', function (data) {
      that.drivingWaitingQueue = that.fetchDrivingQueue()
    })
    this.interval = setInterval(() => {
      that.timestamps = that.drivingWaitingQueue.map(c => getISOFromNow(c.player.register_datetime))
    }, 3000)
  },
  beforeUnmount () {
    clearInterval(this.interval)
  },
  methods: {
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
