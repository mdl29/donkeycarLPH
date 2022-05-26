<template>
<div>
<h1> Donkeycar Dashboard </h1>
    <div class="hidden">
      <vs-sidebar absolute v-model="active" open>
        <template #logo>
          <img class="logo" src="../assets/donkeycar.png">
        </template>
        <vs-sidebar-item id="home">
          <template #icon>
            <i class='bx bx-home'></i>
          </template>
          Home
        </vs-sidebar-item>
        <vs-sidebar-item id="cars">
          <template #icon>
            <i class='bx bx-grid-alt'></i>
          </template>
          voitures
        </vs-sidebar-item>
        <vs-sidebar-item id="waitingList">
          <template #icon>
            <i class='bx bxs-music'></i>
          </template>
          liste d'attente
        </vs-sidebar-item>
      </vs-sidebar>
    </div>
    <div class="table-wrapper" v-if="active === 'waitingList'">
      <vs-table >
        <template #thead>
          <vs-tr>
            <vs-th>
              Ordre
            </vs-th>
            <vs-th>
              Pseudo
            </vs-th>
            <vs-th>
              Id
            </vs-th>
            <vs-th>
              Création
            </vs-th>
          </vs-tr>
        </template>
        <template #tbody>
          <vs-tr v-for="(DrivingContent,i) in drivingWaitingQueue" v-bind:key="DrivingContent.rank" >
            <vs-td>
              {{ i }}
            </vs-td>
            <vs-td>
            {{ DrivingContent.player.player_pseudo }}
            </vs-td>
            <vs-td>
              <p class="id-text"> {{ DrivingContent.player_id }} </p>
            </vs-td>
            <vs-td>
             <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg> {{getISOFromNow(DrivingContent.player.register_datetime)}}
            </vs-td>
            <template #expand>
              <div class="expand-content">
                <div class="button-wrapper" >
                  <vs-row>
                    <vs-col vs-justify="center" vs-align="center" w="2">
                      <vs-button color="#7d33ff" relief @click="paramPlayerDialog = true; playerSpec = DrivingContent.player; parPlayerPseudo = DrivingContent.player.player_pseudo">
                        Player parameters
                      </vs-button>
                    </vs-col>
                    <vs-col vs-justify="center" vs-align="center" w="2">
                      <vs-button border danger>
                        Remove this player
                      </vs-button>
                    </vs-col>
                  </vs-row>
                </div>
              </div>
            </template>
          </vs-tr>
        </template>
      </vs-table>
    </div>
    <div class="cards-wrapper" v-if="active === 'cars'">
      <vs-card-group>
        <vs-card :key="i" v-for="(car, i) in cars" :data="car">
          <template #title>
            <h3>{{car.name}}</h3>
          </template>
          <template #text>
            <p> IP : {{car.ip}} </p>
            <div class="center grid">
              <vs-row>
                <vs-col class="text-status" vs-type="flex" vs-justify="right" vs-align="right" w="6">
                  <p>Status : </p>
                </vs-col>
                <vs-col vs-type="flex" vs-justify="right" vs-align="right" w="6">
                  <vs-button color="#00b4d8" v-if="car.status === 'DRIVE'" > 🎮 Drive </vs-button>
                  <vs-button color="#8338ec" v-if="car.status === 'RECORING'" > 🎥 recording data </vs-button>
                  <vs-button color="#06d6a0" v-if="car.status === 'AI_ASSISTED'" > 🧪 AI assisted </vs-button>
                  <vs-button color="#fe5f55" v-if="car.status === 'MAINTAINANCE'" > 🧰 In maintainance </vs-button>
                </vs-col>
              </vs-row>
              <p v-if="car.user!=''"> Used by : <b>{{car.user}}</b> </p>
              <vs-button class="param-btn" warn @click=" carSpec={car} ; parampopup=true"> <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" style="fill: rgba(0, 0, 0, 1);transform: ;msFilter:;"><path d="M13 5h9v2h-9zM2 7h7v2h2V3H9v2H2zm7 10h13v2H9zm10-6h3v2h-3zm-2 4V9.012h-2V11H2v2h13v2zM7 21v-6H5v2H2v2h3v2z"></path></svg> </vs-button>
            </div>
          </template>
        </vs-card>
      </vs-card-group>
     </div>
      <vs-dialog v-model="paramPlayerDialog">
        <template #header>
          <h4 class="not-margin">
            Welcome to <b>{{playerSpec.player_pseudo}}</b> parameters
          </h4>
        </template>
        <div class="con-form">
          <vs-input class="param-input" label="Pseudo" v-model="parPlayerPseudo"/>
          <vs-input class="param-input" label="move before :" v-model="moveBeforeInput" placeholder="player id" />
          <vs-input class="param-input" label="move after :" v-model="moveAfterInput" placeholder="player id"/>
        </div>

        <template #footer>
          <div class="footer-dialog">
            <vs-button block success @click="postNewParams(playerSpec)">
              Save parameters
            </vs-button>
          </div>
        </template>
      </vs-dialog>
</div>
</template>
<script>
import DonkeycarManagerService from '@/js/service.js'

const { io } = require('socket.io-client')
const moment = require('moment')

moment.locale('fr')

const ip = 'localhost'
const srv = new DonkeycarManagerService('http://' + ip + ':8000')
var socket = io.connect('http://' + ip + ':8000', { path: '/ws/socket.io' })

export default {
  data: () => ({
    paramPlayerDialog: false,
    playerSpec: {},
    parPlayerPseudo: '',
    moveBeforeInput: '',
    moveAfterInput: '',
    parampopup: false,
    carSpec: {},
    active: 'home',
    drivingWaitingQueue: []
  }),
  mounted () {
    this.fetchDrivingQueue()
  },
  created () {
    const that = this
    socket.on('driveWaitingPool.updated', function (data) {
      that.drivingWaitingQueue = data.drivePlayersWaitingPool
    })
  },
  methods: {
    async fetchPlayers () {
      this.poolPlayers = await srv.getAllplayers(0, 20)
    },
    async fetchDrivingQueue () {
      this.drivingWaitingQueue = await srv.getDrivingWaitingQueue(true, 0, 20)
    },
    getISOFromNow (iso) {
      const date = new Date(iso)
      const timestamp = date.getTime()
      const fromNow = moment(timestamp).fromNow()
      return fromNow
    },
    async postNewParams (currentplayer) {
      this.paramPlayerDialog = false
      if (this.parPlayerPseudo !== currentplayer.player_pseudo) {
        await srv.updatePlayerPseudo(currentplayer, this.parPlayerPseudo)
      }
      if (this.moveBeforeInput !== '') {
        await srv.moveBefore(currentplayer.player_id, this.moveBeforeInput)
        this.moveBeforeInput = ''
      }
      if (this.moveAfterInput !== '') {
        await srv.moveAfter(currentplayer.player_id, this.moveAfterInput)
        this.moveAfterInput = ''
      }
    }
  }
}
</script>

<style>
.param-input{
  padding-bottom: 35px;
}
.vs-card-content{
  width:300px !important ;
}
.text-status{
  padding-top:10px;
  /* text-align: right; */
  font-size: 15px;
}
.cards-wrapper{
  padding-left: 260px;
}
.table-wrapper{
    padding-left: 260px;
    text-align: left !important;
}
.logo{
    width: 175px;
}
.id-text{
  color: #ae2012 ;
  font-weight: bold;
}
</style>
