<template>
    <div class="header">
        <h1 class="mainTitle">Donkeycar dashboard</h1>
    </div>
    <div class="mainContainer">
      <div class="carColumn">
        <carInfo v-for="car in cars" :key="car.worker_id" :car="car"></carInfo>
      </div>
      <div class="waitingJobsColumn">
        <waitingJobCard v-for="job in waitingJobs" :key="job.rank" :job="job" @goUp="goUp($event)" @goDown="goDown($event)" @remove="removeJob($event)"></waitingJobCard>
      </div>
      <div class="runningJobsColumn">
        <runningJobCard v-for="job in runningJobs" :key="job.worker_id" :job="job" :reload="reload" :carColor="getCarColor(job.worker_id)" :carName="getCarName(job.worker_id)" @resume="resumeJob($event)" @reload="reloadJob($event)"></runningJobCard>
      </div>
    </div>
</template>
<script>
import carInfo from '@/components/carInfo.vue'
import DonkeycarManagerService from '@/js/service.js'
import waitingJobCard from '@/components/waitingJob.vue'
import runningJobCard from '@/components/runningJobCard.vue'

const { io } = require('socket.io-client')

const ip = DonkeycarManagerService.ip
const srv = new DonkeycarManagerService('http://' + ip + ':8000')
const socket = io.connect('http://' + ip + ':8000', { path: '/ws/socket.io' })

export default {
  components: {
    carInfo,
    waitingJobCard,
    runningJobCard
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
      that.getRunningJobs()
    })
  },
  mounted () {
    this.fetchcars()
    this.fetchWaitingJobs()
    this.getRunningJobs()
  },
  data () {
    return {
      cars: [],
      waitingJobs: [],
      runningJobs: [],
      reload: false
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
      if (index !== -1) {
        const playerBefore = this.waitingJobs[index]
        await srv.moveBefore(job.job_id, playerBefore.job_id)
      }
    },
    async goDown (job) {
      const index = this.waitingJobs.indexOf(job) + 1
      if (this.waitingJobs.length > index) {
        const playerBefore = this.waitingJobs[index]
        await srv.moveAfter(job.job_id, playerBefore.job_id)
      }
    },
    async removeJob (job) {
      await srv.removeJob(job)
    },
    async getRunningJobs () {
      this.runningJobs = await srv.getRunningJobs()
    },
    getCarName (id) {
      for (const car of this.cars) {
        if (car.worker_id === id) {
          return car.name
        }
      }
      return 'unknow car'
    },
    getCarColor (id) {
      for (const car of this.cars) {
        if (car.worker_id === id) {
          return car.color
        }
      }
      return 'unknow color'
    },
    async resumeJob (job) {
      await srv.resumeJob(job)
    },
    async reloadJob (job) {
      this.reload = true
      await srv.addJobs(job.player_id, job.worker_id)
      const firstJob = await srv.getDrivingWaitingQueue(true, 0, 1)
      await srv.moveBefore(job.job_id, firstJob[0].job_id)
      await srv.removeJob(job)
      this.reload = false
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
.waitingwaitingJobsColumn{
    order: 2;
    flex-wrap: wrap;
}
</style>
