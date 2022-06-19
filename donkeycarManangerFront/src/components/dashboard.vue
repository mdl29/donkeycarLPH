<template>
<div>
    <div class="hidden">
      <vs-sidebar absolute v-model="active" open class="slide-bar">
        <template #logo>
          <img class="logo" src="../assets/donkeycar.png">
        </template>
        <vs-sidebar-item id="home">
          HOME
        </vs-sidebar-item>
        <vs-sidebar-item id="cars">
          CARS
        </vs-sidebar-item>
        <vs-sidebar-item id="waitingList">
          WAITING LIST
        </vs-sidebar-item>
          <vs-sidebar-item id="jobs">
          <template #icon>
            🚀
          </template>
          WAITING LIST
        </vs-sidebar-item>
      </vs-sidebar>
    </div>
    <div class="table-wrapper" v-if="active === 'home'">
      <div class="pl-data-wrapper">
        <h1> Donkeycar Dashboard </h1>
        <h3> data :</h3>
        <p> Users in waitingList : {{this.drivingWaitingQueue.length}}</p>
        <p> total users : {{this.allPlayers.length}}</p>
      </div>
    </div>
    <div class="table-wrapper" v-if="active === 'waitingList'">
      <h1 class="title-dash"> Donkeycar Dashboard </h1>
      <vs-table >
        <template #thead>
          <vs-tr>
            <vs-th>
              order
            </vs-th>
            <vs-th>
              username
            </vs-th>
            <vs-th>
              Job ID
            </vs-th>
            <vs-th>
              created ago
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
              <p class="id-text"> {{ DrivingContent.job_id }} </p>
            </vs-td>
            <vs-td>
             <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg> {{getISOFromNow(DrivingContent.player.register_datetime)}}
            </vs-td>
            <template #expand>
              <div class="expand-content">
                <div class="button-wrapper" >
                  <vs-row>
                    <vs-col vs-justify="center" vs-align="center" w="2">
                      <vs-button color="#7d33ff" relief @click="paramPlayerDialog = true; playerSpec = DrivingContent; parPlayerPseudo = DrivingContent.player.player_pseudo">
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
      <h1 class="title-dash"> Donkeycar Dashboard </h1>
        <h4 style="display: inline-flex;">
        <vs-card :key="car.name" v-for="car in donkeycars" :data="car">
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
                <vs-col vs-type="flex" vs-justify="left" vs-align="left" w="6">
                  <vs-button color="#00b4d8" v-if="car.current_stage === 'DRIVE'" > 🎮 Drive </vs-button>
                  <vs-button color="#8338ec" v-if="car.current_stage === 'RECORING'" > 🎥 recording data </vs-button>
                  <vs-button color="#06d6a0" v-if="car.current_stage === 'AI_ASSISTED'" > 🧪 AI assisted </vs-button>
                  <vs-button color="#fe5f55" v-if="car.current_stage === 'MAINTENANCE'" > 🧰 Maintenance </vs-button>
                  <vs-button color="#fe5f55" v-if="car.current_stage === null" > ❌ no status </vs-button>
                </vs-col>
              </vs-row>
              <p v-if="car.current_player_id!=null"> Used by : <b>{{car.player.player_pseudo}}</b> </p>
              <p v-else> Used by : <b>nobody</b> </p>
              <vs-row class="popup-footer">
                <vs-col vs-type="flex" w="4">
                  <vs-button class="param-btn" warn @click=" carSpec=car ; parampopup=true ; newStatus = carSpec.current_stage ; calibValue =1; carPlayer = carSpec.current_player_id"> <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" style="fill: rgba(0, 0, 0, 1);transform: ;msFilter:;"><path d="M13 5h9v2h-9zM2 7h7v2h2V3H9v2H2zm7 10h13v2H9zm10-6h3v2h-3zm-2 4V9.012h-2V11H2v2h13v2zM7 21v-6H5v2H2v2h3v2z"></path></svg> </vs-button>
                </vs-col>
                <vs-col vs-type="absolute" w="4" vs-justify="center" vs-align="center" >
                  <vs-button danger class="engine-button"> Stop engines</vs-button>
                </vs-col>
                <vs-col vs-type="absolute" w="4">
                  <vs-avatar class="avatar-color" :color="'#'+car.color"> <template #text> Color </template> </vs-avatar>
                </vs-col>
              </vs-row>
            </div>
          </template>
        </vs-card>
        </h4>
     </div>
      <vs-dialog v-model="parampopup" style="display:flex;">
        <template #header>
          <h4 class="not-margin">
            Welcome to <b>{{carSpec.name}}</b> parameters
          </h4>
        </template>

        <template #footer>
          <div class="center-box">
            <vs-select class="param-input" placeholder="Select a throttle pourcent" v-model="calibValue" label="throttle calibration">
              <vs-option label="100 %" value="1">
                100%
              </vs-option>
              <vs-option label="75 %" value="0.75">
                75%
              </vs-option>
              <vs-option label="50 %" value="0.5">
                50%
              </vs-option>
              <vs-option  label="25 %" value="0.25">
                25%
              </vs-option>
            </vs-select>
            <vs-select class="param-input" placeholder="Change current stage" v-model="newStatus" label="change car stage" >
              <vs-option label="DRIVE" value="DRIVE">
                DRIVE
              </vs-option>
              <vs-option label="AI_ASSISTED" value="AI_ASSISTED">
                AI_ASSISTED
              </vs-option>
              <vs-option label="MAINTENANCE" value="MAINTENANCE">
                MAINTENANCE
              </vs-option>
              <vs-option  label="RECORING" value="RECORING">
                RECORING
              </vs-option>
              <vs-option  label="null" value=null>
                null
              </vs-option>
            </vs-select>
            <vs-input class="param-input" label="Change current player" v-model="carPlayer" placeholder="player id" />
            <vs-button block success @click="postNewCarParam (carSpec, newStatus, carPlayer)">
              Save parameters
            </vs-button>
          </div>
        </template>
      </vs-dialog>
      <vs-dialog v-model="paramPlayerDialog">
        <template #header>
          <h4 class="not-margin">
            Welcome to <b>{{playerSpec.player.player_pseudo}}</b> parameters
          </h4>
        </template>
        <div class="con-form">
          <vs-input class="param-input" label="Pseudo" v-model="parPlayerPseudo"/>
          <vs-input class="param-input" label="move before :" v-model="moveBeforeInput" placeholder="jobs id" />
          <vs-input class="param-input" label="move after :" v-model="moveAfterInput" placeholder="jobs id"/>
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
    carPlayer: '',
    calibValue: '1',
    newStatus: '',
    playerSpec: {},
    parPlayerPseudo: '',
    moveBeforeInput: '',
    moveAfterInput: '',
    parampopup: false,
    carSpec: {},
    active: 'home',
    drivingWaitingQueue: [],
    allPlayers: [],
    donkeycars: []
  }),
  mounted () {
    this.fetchDrivingQueue()
    this.fetchcars(0, 4)
    this.getAllPlayers()
  },
  created () {
    const that = this
    socket.on('driveWaitingPool.updated', function (data) {
      that.drivingWaitingQueue = data.drivePlayersWaitingPool
      that.getAllPlayers()
    })
    socket.on('car.updated', function (data) {
      that.donkeycars = that.fetchcars(0, 4)
    })
  },
  methods: {
    async getPlayer (id) {
      const player = await srv.getplayer(id)
      return player
    },
    async getAllPlayers () {
      this.allPlayers = await srv.getAllPlayers()
    },
    async fetchDrivingQueue () {
      this.drivingWaitingQueue = await srv.getDrivingWaitingQueue(true, 0, 20)
    },
    async fetchcars (skip, limit) {
      this.donkeycars = await srv.getCars(skip, limit)
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
        await srv.moveBefore(currentplayer.job_id, this.moveBeforeInput)
        this.moveBeforeInput = ''
      }
      if (this.moveAfterInput !== '') {
        await srv.moveAfter(currentplayer.job_id, this.moveAfterInput)
        this.moveAfterInput = ''
      }
    },
    async postNewCarParam (car, newStatus, carPlayer) {
      if (newStatus === 'MAINTENANCE') {
        carPlayer = null
      }
      if (carPlayer === 'null') {
        carPlayer = null
      }
      await srv.updateCar(car, newStatus, carPlayer)
      this.parampopup = false
    }
  }
}
</script>

<style>
.popup-footer{
  padding-top: 30px;
}
.engine-button{
  font-weight: bold;
  width: 100%;
}
.avatar-color{
  position: relative;
  float: right;
}
.center-box{
  text-align: center ;
  align-items: center ;
  display:block;
}
.title-dash{
  text-align: center;
}
.pl-data-wrapper{
  text-align: center;
}
.slide-bar{
  width: 170px !important;
}
.param-input{
  padding-bottom: 35px;
}
.vs-card-content{
  width:300px !important ;
}
.text-status{
  padding-top:10px;
  text-align: right;
  font-size: 15px;
}
.cards-wrapper{
  padding-left: 180px;
}
.table-wrapper{
    padding-left: 180px;
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
