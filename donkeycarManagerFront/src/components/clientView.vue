<template>
<div>
<div style="height: 600px; padding-top: 0px;">
    <div style="height: 82%; margin-top: 0px;">
        <!-- If have two players-->
        <vs-row>
            <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="6" class="pilot1-wrapper" >
            <!-- Player 1 -->
            <div v-if="car1 === null || car1.current_race_id === null || job1[0] === undefined"> <!-- No player assigned, display waiting message -->
              <h1> Player 1</h1>
               <div class="attente-text">
                <span style="--i:1">E</span>
                <span style="--i:2">N</span>
                <span style="--i:3"> </span>
                <span style="--i:4"> </span>
                <span style="--i:5">A</span>
                <span style="--i:6">T</span>
                <span style="--i:7">T</span>
                <span style="--i:8">E</span>
                <span style="--i:9">N</span>
                <span style="--i:10">T</span>
                <span style="--i:11">E</span>
                <span style="--i:12">.</span>
                <span style="--i:13">.</span>
                <span style="--i:14">.</span>
               </div>
            </div>
            <div v-if="car1 !== null">
              <div v-if="car1.race">
                  <vs-button  size="xl" :color="'#'+car1.color" class="car-name-button"> {{car1.name}}</vs-button>
                  <h1 v-if="job1[0].player.player_pseudo !== undefined"> {{ job1[0].player.player_pseudo}}</h1>
                  <h1 v-if="job1[0].player.player_pseudo === undefined"> Unknow player</h1>
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
                          <vs-tr v-for="(lap, i) in car1.race.laptimers" v-bind:key="lap.laptimer_id">
                              <vs-td>
                                  {{i+1}}
                              </vs-td>
                              <vs-td>
                                  {{lap.duration/1000}} s
                              </vs-td>
                          </vs-tr>
                          </template>
                      </vs-table>
                      <h4 v-if="car1.race.laptimers.length > 0" class="best-score-text">Meilleur temps : {{getBestScore(car1.race.laptimers)}}s</h4>
                  </div>
                    <div class="video-wrapper">
                    <img id='mpeg-image' class='img-responsive' :src="'http://'+ car1.ip + ':8887/video'"/>
                  </div>
              </div>
              <div v-else>
                  <vs-button  size="xl" :color="'#'+car1.color" class="car-name-button"> {{car1.name}}</vs-button>
                  <template v-if="job1[0]">
                    <h1 v-if="job1[0].player.player_pseudo !== undefined"> {{ job1[0].player.player_pseudo}}</h1>
                    <h1 v-if="job1[0].player.player_pseudo === undefined"> Unknow player</h1>
                    <div class="no-laptimer-wrapper">
                        <h3 class='no-laptimer-text'> Veuillez avancer pour lancer la course</h3>
                    </div>
                  </template>
                  <template v-else>
                    <h1>Pas de joueur</h1>
                  </template>
              </div>
            </div>
            </vs-col>

            <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="6" class="pilot-wrapper">
              <!-- Player 2 -->
              <div v-if="car2 === null || car2.current_race_id === null || job2[0] === undefined">
              <h1> Player 2</h1>
               <div class="attente-text">
                <span style="--i:1">E</span>
                <span style="--i:2">N</span>
                <span style="--i:3"> </span>
                <span style="--i:4"> </span>
                <span style="--i:5">A</span>
                <span style="--i:6">T</span>
                <span style="--i:7">T</span>
                <span style="--i:8">E</span>
                <span style="--i:9">N</span>
                <span style="--i:10">T</span>
                <span style="--i:11">E</span>
                <span style="--i:12">.</span>
                <span style="--i:13">.</span>
                <span style="--i:14">.</span>
               </div>
            </div>
            <div v-if="car2 !== null">
              <div v-if="car2.race && car2.race.laptimers.length !== 0">
                  <vs-button  size="xl" :color="'#'+car1.color" class="car-name-button"> {{car1.name}}</vs-button>
                  <h1 v-if="job2[0].player.player_pseudo !== undefined"> {{ job2[0].player.player_pseudo}}</h1>
                  <h1 v-if="job2[0].player.player_pseudo === undefined"> Unknow player</h1>
                  <div>
                      <vs-table class="table-head"  v-if="car2.race !== null && car2.race.laptimers !== undefined" >
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
                          <vs-tr v-for="(lap, i) in car2.race.laptimers" v-bind:key="lap.laptimer_id">
                              <vs-td>
                                  {{i+1}}
                              </vs-td>
                              <vs-td>
                                  {{lap.duration/1000}} s
                              </vs-td>
                          </vs-tr>
                          </template>
                      </vs-table>
                      <h4 v-if="car2.race.laptimers.length > 0" class="best-score-text">Meilleur temps : {{getBestScore(car2.race.laptimers)}}s</h4>
                  </div>
                    <div class="video-wrapper">
                    <img id='mpeg-image' class='img-responsive' :src="'http://'+ car1.ip + ':8887/video'"/>
                  </div>
              </div>
              <div v-else>
                  <vs-button  size="xl" :color="'#'+car2.color" class="car-name-button"> {{car2.name}}</vs-button>
                  <template v-if="job2[0]">
                    <h1 v-if="job2[0].player.player_pseudo !== undefined"> {{ job2[0].player.player_pseudo}}</h1>
                    <h1 v-if="job2[0].player.player_pseudo === undefined"> Unknow player</h1>
                    <div class="no-laptimer-wrapper">
                        <h3 class='no-laptimer-text'> Veuillez avancer pour lancer la course</h3>
                    </div>
                  </template>
                  <template v-else>
                    <h1> Pas de joueur</h1>
                  </template>
            </div>
            </div>
            </vs-col>
        </vs-row>
    </div>
  </div>
  <div style="height: 18%; margin-bottom: 0px;" >
      <vs-row>
      <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="4" v-if="car1 !== null && car1.race != undefined">
        <flip-countdown v-if="car1.race && car1.race.start_datetime" class="flip-countdown" :deadline="makeDate(car1.race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
        <flip-countdown  v-if="car1.race === null" class="flip-countdown" deadline="2018-06-06 21:20:36" :showDays="false" :showHours="false" ></flip-countdown> <!-- why is it here ??-->
      </vs-col>
      <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="4" v-if="waitingList !== undefined || waitingList !== []">
        <vs-table class="waiting-table" v-if="waitingList !== undefined">
          <template #thead>
          <vs-tr>
              <vs-th>
              Ordre
              </vs-th>
              <vs-th>
              Pseudo
              </vs-th>
              <vs-th>
              Attente estimée
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
               <p v-if=" i+1 <= 2"> 15 minutes</p>
               <p v-if=" i+1 > 2 && i+1 <= 4"> 30 minutes</p>
               <p v-if=" i+1 > 4 && i+1 <= 4"> 45 minutes</p>
              </vs-td>
          </vs-tr>
          </template>
        </vs-table>
      </vs-col>
      <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="4" v-if="car2 !== null">
        <flip-countdown v-if="car2.race !== null && car2.race !== undefined && car2.race.start_datetime !== undefined" class="flip-countdown" :deadline="makeDate(car2.race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
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
    car1: null,
    car2: null,
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
      console.debug('clientView.event: car.updated')
      that.fetchcars(0, 4)
    })
    socket.on('car.added', function (data) {
      console.debug('clientView.event: car.added')
      that.fetchcars(0, 4)
    })
    socket.on('laptimer.added', function (data) {
      console.debug('clientView.event: laptimer.added')
      that.fetchcars(0, 4)
    })
    socket.on('jobs.all.updated', function (data) {
      console.debug('clientView.event: jobs.all.updated')
      that.fetchWaitinPlayers()
      that.fetchcars(0, 4)
    })
    socket.on('worker.all.updated', function (data) {
      console.debug('clientView.event: worker.all.updated')
      that.fetchWaitinPlayers()
      that.fetchcars(0, 4)
    })
  },
  methods: {
    async fetchcars (skip, limit) {
      const cars = await srv.getCars(skip, limit)
      this.cars = cars
      for (const car of cars) {
        console.debug('clientView: car %o', car)
        if (car.worker.state === 'BUSY' || car.worker.state === 'AVAILABLE') {
          if (this.car1 === null || (this.car1 !== null && this.car1.name === car.name)) {
            this.car1 = car
            console.debug('clientView: displaying car %s (%s) as first (left side car)', car.name, car.worker.state)
            this.job1 = await srv.getJobCar(car.worker_id)
          } else if (this.car2 === null || (this.car2 !== null && this.car2.name === car.name)) {
            this.car2 = car
            console.debug('clientView: displaying car %s (%s) as second (right side car)', car.name, car.worker.state)
            this.job2 = await srv.getJobCar(car.worker_id)
          } else {
            this.car1 = null
            this.car2 = null
            this.job1 = []
            this.job2 = []
          }
        } else if (car.worker.state === 'STOPPED') { // Handle stopped car, remove them if the were displayed
          if (this.car1 && this.car1.name === car.name) { // Stopped car was displayed as car1, removing it
            console.debug('clientView: car %s was stopped, removing it from first (left side car)', car.name)
            this.car1 = null
          }

          if (this.car2 && this.car2.name === car.name) {
            console.debug('clientView: car %s was stopped, removing it from second (right side car)', car.name)
            this.car2 = null
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
 margin-top: 40%;
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
  width: 110%;
  height: 100%;
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
.attente-text {
  margin-top: 40%;
  position: relative;
}
.attente-text span {
  position: relative;
  display: inline-block;
  font-weight: bold;
  font-size: 50px;
  text-transform: uppercase;
  animation: flip 5s infinite;
  animation-delay: calc(.2s * var(--i))
}
@keyframes flip {
  0%,80% {
    transform: rotateY(360deg)
  }
}
.pilot1-wrapper {
  border-right: 2.5px dashed grey;
}
</style>
