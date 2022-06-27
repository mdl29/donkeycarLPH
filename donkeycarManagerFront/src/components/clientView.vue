<template>
<div class="wrapper">
<div class="players-wrapper">
      <vs-row class="cars">
          <car-view :car="car1" :job="job1" number="1" />
          <car-view :car="car2" :job="job2" number="2" />
      </vs-row>
  </div>
  <div>
      <vs-row>
      <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="4" v-if="car1 !== null && car1.race != undefined">
        <flip-countdown v-if="car1.race && car1.race.start_datetime" class="flip-countdown" :deadline="makeDate(car1.race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
        <flip-countdown  v-if="car1.race === null" class="flip-countdown" deadline="2018-06-06 21:20:36" :showDays="false" :showHours="false" ></flip-countdown> <!-- why is it here ??-->
      </vs-col>
      <div class="waiting-list">
        <template v-for="(player,i) in waitingList">
          <div class="row">
              <div v-bind:key="player.rank" class="pseudo">
              {{player.player.player_pseudo}}
              </div>
              <div class="timeleft">
                {{ timeLeft(i) }} min
              </div>
          </div>
        </template>
      </div>
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
import carView from './carView.vue'
import FlipCountdown from 'vue2-flip-countdown'
import moment from 'moment'

const { io } = require('socket.io-client')
const ip = '192.168.20.107'
const srv = new DonkeycarManagerService('http://' + ip + ':8000')
var socket = io.connect('http://' + ip + ':8000', { path: '/ws/socket.io' })

export default {
  components: {
    FlipCountdown,
    carView
  },
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
          if ( this.car1 && this.car1.name === car.name){
            this.car1 = car
          } else if ( this.car2 && this.car2.name === car.name){
            this.car2 = car
          }else{
            if (this.car1 === null){
              this.car1 = car
            }else if (this.car2 === null){
              this.car2 = car
            }else{
              console.warn("too many cars, can't display %s",car.name)
            }
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
      if (this.car1){
        this.job1 = await  srv.getJobCar(this.car1.worker_id)
      }
      if (this.car2){
        this.job2 = await  srv.getJobCar(this.car2.worker_id)
      }
    },
    async fetchWaitinPlayers () {
      this.waitingList = await srv.getDrivingWaitingQueue(true, 0, 12)
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
    getJobDuration(job) {
      if (!job.parameters) {
        return 0;
      }
      return (parseInt(JSON.parse(job.parameters).drive_time) || 0);
    },
    timeLeft (index) {
      const current_job = Math.min(this.getJobDuration(this.job1), this.getJobDuration(this.job2));
      // waitingList is an array of jobs, jobs have a JSON string called parameters that contains the job duration
      return Math.floor((this.waitingList.map((v, i) => i >= index ? 0 : this.getJobDuration(v)).reduce((a, v) => a + v) + current_job) / 60);
    },
    makeDate (myDate) {
      const date = new Date(myDate)
      const trueDate = String(date.getFullYear()) + '-' + String(date.getMonth() + 1) + '-' + String(date.getDate()) + ' ' + String(date.getHours()) + ':' + String(date.getMinutes() + 2) + ':' + String(date.getSeconds())
      console.log(trueDate)
      return trueDate
    },
  }
}
</script>
<style scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.players-wrapper {
  flex: 3;
}
.flip-countdown {
  padding-top: 25px;
}
.waiting-table{
  text-align: left !important;
  width: 110%;
  height: 100%;
}
@keyframes grow-animation {
  0% { transform: scale(1); }
  50% {transform: scale(1.15); }
  100% {transform: scale(1); }
}
.waiting-list {
  display: flex;
  padding-left: 1em;
  padding-top: 1em;
  padding-bottom: 0.5em;
  overflow-x: hidden;
}
.waiting-list::after {
  display: block;
  height: 3em;
  width: 7em;
  background: linear-gradient(to left, white 20%, transparent);
  position: absolute;
  right: 0;
  content: "";
}
.waiting-list .row {
  display: flex;
  background: #4269F5;
  padding-left: 10px;
  border-radius: 2em;
  color: white;
  margin-right: 10px;
  justify-content: space-between;
  align-items: center;
  min-width: 10em;
  white-space: nowrap;
  overflow-x: hidden;
}
.waiting-list .row .pseudo {
  margin-left: 10px;
  font-weight: bold;
  font-size: 1.1em;
  max-width: 5em;
}
.waiting-list .row .timeleft {
  border-radius: 2em;
  padding: 15px;
}
.waiting-list .row:last-child {
  margin-right: 0;
}
.cars {
  display: flex;
  flex-grow: 2;
  height: 100%;
  justify-content: center;
  align-items: center;
}
</style>
