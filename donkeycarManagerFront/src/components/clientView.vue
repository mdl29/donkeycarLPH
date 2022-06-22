<template>
<div>
<div style="height: 600px; padding-top: 0px;">
    <div style="height: 82%; margin-top: 0px;">
        <!-- If have two players-->
        <vs-row>
            <!-- Player 1 -->
            <div v-if="car1.length === [] && job2 === []">
               <h1> En attente d'un nouveau joueur</h1>
            </div>
            <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="6" class="pilot-wrapper" >
              <div v-if="car1.race !== null && car1 !== [] && job1 !== []">
                <vs-button  size="xl" :color="'#'+car1.color" class="car-name-button"> {{car1.name}}</vs-button>
                <h1> {{ job1[0].player.player_pseudo}}</h1>
                <div>
                    <vs-table class="table-head">
                        <template #thead>
                        <vs-tr>
                            <vs-th>
                            Tours
                            </vs-th>
                            <vs-th>
                            Temps
                            </vs-th>
                        </vs-tr>
                        </template>
                        <template #tbody>
                        <vs-tr v-for="(lap,i) in car1.race.laptimers" v-bind:key="i">
                            <vs-td>
                                {{i+1}}
                            </vs-td>
                            <vs-td>
                                {{lap.duration/1000}} s
                            </vs-td>
                        </vs-tr>
                        </template>
                    </vs-table>
                    <h4 v-if="car1.race.laptimers !== []" class="best-score-text">Meilleur temps : {{getBestScore(car1.race.laptimers)}}s</h4>
                </div>
              <div class="video-wrapper">
                <img id='mpeg-image' class='img-responsive' :src="'http://'+ car1.ip + ':8787/video'"/>
              </div>
            </div>
            <div v-if="car1.race === null && job1 !== []">
                <vs-button  size="xl" :color="'#'+car1.color" class="car-name-button"> {{car1.name}}</vs-button>
                <h1> {{ job1[0].player.player_pseudo}}</h1>
                <div class="no-laptimer-wrapper">
                    <h3 class='no-laptimer-text'> Veuillez avancer pour lancer la course</h3>
                </div>
            </div>
            </vs-col>

            <!-- Player 2 -->
              <div v-if="car2 === [] && job2 === []">
                <h1> En attente d'un nouveau joueur</h1>
              </div>
            <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="6" class="pilot-wrapper" v-if="car2.race !== null && car2 !== []">
              <div>
                <vs-button  size="xl" :color="'#'+car2.color" class="car-name-button"> {{car2.name}}</vs-button>
                <h1> {{ job2[0].player.player_pseudo}}</h1>
                <div>
                    <vs-table class="table-head">
                        <template #thead>
                        <vs-tr>
                            <vs-th>
                            Tours
                            </vs-th>
                            <vs-th>
                            Temps
                            </vs-th>
                        </vs-tr>
                        </template>
                        <template #tbody>
                        <vs-tr v-for="(lap,i) in car2.race.laptimers" v-bind:key="i">
                            <vs-td>
                                {{i+1}}
                            </vs-td>
                            <vs-td>
                                {{lap.duration/1000}} s
                            </vs-td>
                        </vs-tr>
                        </template>
                    </vs-table>
                </div>
                <h4 v-if="car2.race.laptimers !== []" class="best-score-text">Meilleur temps : {{getBestScore(car2.race.laptimers)}}s</h4>
                <div class="video-wrapper">
                  <img id='mpeg-image' class='img-responsive' :src="'http://'+ car2.ip + ':8787/video'"/>
                </div>
              </div>

              <div v-if="car2.race === null && job2 !== []" >
                <vs-button  size="xl" :color="'#'+car2.color" class="car-name-button"> {{car2.name}}</vs-button>
                <h1> {{ job2[0].player.player_pseudo}}</h1>
                <div class="no-laptimer-wrapper">
                    <h3 class='no-laptimer-text'> Veuillez avancer pour lancer la course</h3>
                </div>
              </div>

            </vs-col>
        </vs-row>
    </div>
  </div>
  <div style="height: 18%; margin-bottom: 0px;" >
      <vs-row>
      <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="4" v-if="car1.race !== []" >
        <flip-countdown v-if="car1.race !== null" class="flip-countdown" :deadline="makeDate(car1.race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
        <flip-countdown  v-if="car1.race === null" class="flip-countdown" deadline="2018-06-06 21:20:36" :showDays="false" :showHours="false" ></flip-countdown>
      </vs-col>
      <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="4">
        <vs-table class="waiting-table">
          <template #thead>
          <vs-tr>
              <vs-th>
              Ordre
              </vs-th>
              <vs-th>
              Pseudo
              </vs-th>
              <vs-th>
              Passage estimé
              </vs-th>
          </vs-tr>
          </template>
          <template #tbody>
          <vs-tr  v-for="(player,i) in waitingList" v-bind:key="player.rank">
              <vs-td>
              {{i + 1}}
              </vs-td>
              <vs-td>
              {{player.player.player_pseudo}}
              </vs-td>
              <vs-td>
              {{fetchEstimatedPassage(i+1)}}
              </vs-td>
          </vs-tr>
          </template>
        </vs-table>
      </vs-col>
      <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="4" v-if="car2 === []" >
          <p> </p>
      </vs-col>
      <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="4" v-if="car1 === []" >
          <p> </p>
      </vs-col>
      <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="4" >
        <flip-countdown v-if="car2.race !== null" class="flip-countdown" :deadline="makeDate(car2.race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
        <flip-countdown  v-if="car2.race === null" class="flip-countdown" deadline="2018-06-06 21:20:36" :showDays="false" :showHours="false" ></flip-countdown>
      </vs-col>
    </vs-row>
  </div>
</div>
</template>
<script>
import DonkeycarManagerService from '@/js/service.js'
import FlipCountdown from 'vue2-flip-countdown'

const { io } = require('socket.io-client')
const ip = 'localhost'
const srv = new DonkeycarManagerService('http://' + ip + ':8000')
var socket = io.connect('http://' + ip + ':8000', { path: '/ws/socket.io' })

export default {
  components: { FlipCountdown },
  data: () => ({
    cars: [],
    car1: [],
    car2: [],
    job1: [],
    job2: [],
    player1Race: [],
    player2Race: [],
    waitingList: [],
    attente: []

  }),
  mounted () {
    this.fetchcars(0, 4)
    this.fetchWaitinPlayers()
  },
  created () {
    const that = this
    socket.on('car.updated', function (data) {
      that.fetchcars(0, 4)
    })
    socket.on('car.added', function (data) {
      that.fetchcars(0, 4)
    })
    socket.on('laptimer.added', function (data) {
      that.fetchcars(0, 4)
    })
    socket.on('jobs.all.updated', function (data) {
      that.fetchWaitinPlayers()
      that.fetchcars(0, 4)
    })
  },
  methods: {
    async fetchcars (skip, limit) {
      const cars = await srv.getCars(skip, limit)
      this.cars = cars
      for (const car of cars) {
        if (car.current_stage !== 'MAINTENANCE' && car.worker.state === 'AVAILABLE') {
          if (this.car1.length === 0) {
            this.car1 = car
            this.job1 = await srv.getJobCar(car.worker_id)
          } else if (this.car1.length !== 0) {
            this.car2 = car
            this.job2 = await srv.getJobCar(car.worker_id)
          } else {
            this.car1 = []
            this.car2 = []
            this.job1 = []
            this.job2 = []
          }
        }
      }
    },
    async fetchWaitinPlayers () {
      this.waitingList = await srv.getDrivingWaitingQueue(true, 0, 5)
    },
    fetchEstimatedPassage (i) {
      if (i <= 2) {
        const date = String(new Date().getHours()) + ':' + String(new Date().getMinutes() + 15)
        return date
      } else if (i > 2 && i <= 4) {
        const date = String(new Date().getHours()) + ':' + String(new Date().getMinutes() + 30)
        return date
      } else if (i > 4) {
        const date = String(new Date().getHours()) + ':' + String(new Date().getMinutes() + 45)
        return date
      }
    },
    async fetchRaces (skip, limit) {
      const races = await srv.fetchRaces(skip, limit)
      console.log(races[0].player_id)
      console.log(this.car2.player.player_id)
      for (const race of races) {
        if (race.player_id === this.car1.player.player_id) {
          this.player1Race = race
        } else if (race.player_id === this.car2.player.player_id) {
          this.player2Race = race
        }
      }
    },
    makeDate (myDate) {
      const date = new Date(myDate)
      const trueDate = String(date.getFullYear()) + '-' + String(date.getMonth() + 1) + '-' + String(date.getDate()) + ' ' + String(date.getHours()) + ':' + String(date.getMinutes() + 5) + ':' + String(date.getSeconds())
      console.log(trueDate)
      return trueDate
    },
    getBestScore (laptimers) {
      let durations = []
      for (const lap of laptimers) {
        durations.push(lap.duration)
        console.log(lap.duration)
      }
      console.log(durations)
      const bestScore = Math.min.apply(Math, durations)
      console.log(bestScore / 1000)
      return bestScore / 1000
    }
  }
}
</script>
<style>
.no-laptimer-text{
 padding-top: 20px;
 font-size: 25px;
 animation: grow-animation 1s linear infinite;
}

.best-score-text{
 font-size: 15px;
 animation: grow-animation 1s linear infinite;
}

.flip-countdown {
  padding-top: 25px;
}

.waiting-table{
  text-align: left !important;
  width: 100%;
}

.table-head{
  text-align: left !important;
}

@keyframes grow-animation {
  0% { transform: scale(1); }
  50% {transform: scale(1.15); }
  100% {transform: scale(1); }
}

.car-name-button{
    float: right;
}
.video-wrapper{
  padding-top: 15px;
  height: 300px;
  width: 90%;
  display: flex;
  justify-content: center;
}
#mpeg-image{
  width:100%;
  height:100%;
}
</style>
