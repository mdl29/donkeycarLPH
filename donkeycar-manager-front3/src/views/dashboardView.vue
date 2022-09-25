<template>
    <div class="header">
        <h1 class="mainTitle">Donkeycar dashboard</h1>
    </div>
    <div class="mainContainer">
      <div class="carColumn">
        <carInfo v-for="car in cars" :key="car.worker_id" :car="car"></carInfo>
      </div>
      <div class="jobsColumn">
        <waitingJob v-for="job in waitingJobs" :key="job.rank" :job="job" ></waitingJob>
      </div>
    </div>
</template>
<script>
import carInfo from '@/components/carInfo.vue'
import DonkeycarManagerService from '@/js/service.js'
import waitingJob from '@/components/waitingJob.vue'

const { io } = require('socket.io-client')

const ip = DonkeycarManagerService.ip
const srv = new DonkeycarManagerService('http://' + ip + ':8000')
const socket = io.connect('http://' + ip + ':8000', { path: '/ws/socket.io' })

export default {
  components: {
    carInfo,
    waitingJob
  },
  created () {
    const that = this
    socket.on('car.updated', function (data) {
      that.fetchcars()
    })
    socket.on('car.added', function (data) {
      that.fetchcars()
    })
    socket.on('jobs.all.updated', function (data) {
      that.fetchWaitingJobs()
    })
  },
  watch: {
    papa: function () {
      console.log('dssd')
    }
  },
  mounted () {
    this.fetchcars()
    this.fetchWaitingJobs()
  },
  data () {
    return {
      cars: [],
      waitingJobs: []
    }
  },
  methods: {
    async fetchcars () {
      this.cars = await srv.getCars(0, 4)
    },
    async fetchWaitingJobs () {
      this.waitingJobs = await srv.getDrivingWaitingQueue(true, 0, 20)
    },
    async goUp (job) {
      const index = this.waitingJobs.indexOf(job) - 1
      const playerBefore = this.waitingJobs[index]
      await srv.moveBefore(job.job_id, playerBefore.job_id)
    },
    async goDown (job) {
      const index = this.waitingJobs.indexOf(job) + 1
      const playerBefore = this.waitingJobs[index]
      await srv.moveAfter(job.job_id, playerBefore.job_id)
    }
  }
}

</script>
<style>
.header{
    width: 100%;
    height: 15%;
}

.mainTitle{
  margin-top: 1% ;
  font-size: 25px;
}
.mainContainer{
  display: flex;}

.carColumn{
    order: 1;
}
.jobsColumn{
    order: 2;
    flex-wrap: wrap;
}
</style>
