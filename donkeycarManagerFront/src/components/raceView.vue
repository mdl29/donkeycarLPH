<template>
<div>
  <vs-row>
        <vs-col v-if="player2.length == 0 && player1.length !== 0" vs-type="flex" vs-justify="center" vs-align="center" w="12" class="player-wrapper">
          <h1> Course de {{player1.player_pseudo}} </h1>
          <vs-table class="laps-table">
              <template #thead>
              <vs-tr>
                  <vs-th>
                  tours
                  </vs-th>
                  <vs-th>
                  temps
                  </vs-th>
              </vs-tr>
              </template>
              <template #tbody>
              <vs-tr :key="i" v-for="(laps,i) in player1Race.laptimers">
                  <vs-td>
                  {{ i + 1}}
                  </vs-td>
                  <vs-td>
                  {{ laps.duration / 1000 }} s
                  </vs-td>
              </vs-tr>
              </template>
          </vs-table>
          <div class="countdown-wrapper">
            <flip-countdown :deadline="makeDate(player1Race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
          </div>
      </vs-col>
      <vs-col v-if="player2.length !== 0 && player1.length !== 0" vs-type="flex" vs-justify="center" vs-align="center" w="6" class="player-wrapper">
          <h1> Course de {{player1.player_pseudo}} </h1>
          <vs-table class="laps-table">
              <template #thead>
              <vs-tr>
                  <vs-th>
                  tours
                  </vs-th>
                  <vs-th>
                  temps
                  </vs-th>
              </vs-tr>
              </template>
              <template #tbody>
              <vs-tr :key="i" v-for="(laps,i) in player1Race.laptimers">
                  <vs-td>
                  {{ i + 1}}
                  </vs-td>
                  <vs-td>
                  {{ laps.duration / 1000 }} s
                  </vs-td>
              </vs-tr>
              </template>
          </vs-table>
          <div class="countdown-wrapper">
            <flip-countdown :deadline="makeDate(player2Race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
          </div>
      </vs-col>
      <vs-col v-if="player2.length !== 0 && player1.length !== 0" vs-type="flex" vs-justify="center" vs-align="center" w="6" class="player-wrapper">
          <h1> Course de {{player2.player_pseudo}} </h1>
          <vs-table class="laps-table">
              <template #thead>
              <vs-tr>
                  <vs-th>
                  tours
                  </vs-th>
                  <vs-th>
                  temps
                  </vs-th>
              </vs-tr>
              </template>
              <template #tbody>
              <vs-tr :key="i" v-for="(laps,i) in player2Race.laptimers">
                  <vs-td>
                  {{ i + 1}}
                  </vs-td>
                  <vs-td>
                  {{ laps.duration / 1000 }} s
                  </vs-td>
              </vs-tr>
              </template>
          </vs-table>
          <div class="countdown-wrapper">
            <flip-countdown v-if="player2Race.length !== 0 " :deadline="makeDate(player2Race.start_datetime)" :showDays="false" :showHours="false" ></flip-countdown>
          </div>
      </vs-col>
  </vs-row>
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

export default {
  components: { FlipCountdown },
  data: () => ({
    player1: [],
    player2: [],
    player1Race: [],
    player2Race: [],
    cars: []
  }),
  created () {
    const that = this
    socket.on('laptimer.added', function (data) {
      that.fetchRaces(0, 20)
      that.fetchcars(0, 20)
    })
    socket.on('car.updated', function (data) {
      that.fetchcars(0, 20)
      that.fetchRaces(0, 20)
    })
  },
  mounted () {
    this.fetchcars(0, 20)
    this.fetchRaces(0, 20)
  },
  methods: {
    async getPlayer (id) {
      const currentPlayer = await srv.getPlayer(id)
      this.player = currentPlayer
    },
    async fetchcars (skip, limit) {
      const cars = await srv.getCars(skip, limit)
      this.cars = cars
      for (const car of cars) {
        if (car.current_stage !== 'MAINTENANCE') {
          if (this.player1.length === 0) {
            this.player1 = car.player
          } else {
            this.player2 = car.player
          }
        }
      }
    },
    async fetchRaces (skip, limit) {
      const races = await srv.fetchRaces(skip, limit)
      for (const race of races) {
        if (race.player_id === this.player1.player_id) {
          this.player1Race = race
        } else {
          this.player2Race = race
        }
      }
    },
    makeDate (myDate) {
      const days = myDate.slice(0, 10)
      const time = myDate.slice(11, 19)
      if ((parseInt(time.slice(3, 5)) + 5) < 60) {
        const newTime = time.slice(0, 3) + String(parseInt(time.slice(3, 5)) + 5) + time.slice(5, 8)
        console.log(days + ' ' + newTime)
        return days + ' ' + newTime
      } else {
        const newminutes = String(parseInt(time.slice(3, 5)) - 55)
        const hours = String(parseInt(time.slice(0, 2)) + 1)
        return days + ' ' + hours + ':' + newminutes + ':' + time.slice(6, 9)
      }
    }
  }
}

</script>
<style>
.countdown-wrapper{
  padding-top: 45px;
}
.player-wrapper{
  padding: 10px;
}
.laps-table{
  text-align: left;
}
</style>
