<template>
  <div class="header">
        <h5 class="mainTitle">Donkeycar dashboard</h5>
  </div>
  <div class="jobs-card">
    <div class="cars">
        <carInfo v-for="car in cars" :key="car.worker_id" :car="car" class="gutter--md"></carInfo>
    </div>
    <div class="jobs-wrap">
      <div class="jobs">
        <waitingJobCard v-for="job in waitingJobs" :key="job.rank" :job="job" @goUp="goUp($event)" @goDown="goDown($event)" @remove="removeJob($event)" class="gutter--md"></waitingJobCard>
      </div>
      <div class="jobs-over"></div>
    </div>
    <div class="running-jobs">
        <runningJobCard v-for="job in runningJobs" :key="job.worker_id" :job="job" :reload="reload" :carColor="getCarColor(job.worker_id)" :carName="getCarName(job.worker_id)" @resume="resumeJob($event)" @reload="reloadJob($event)" @record="addRecord($event)" class="gutter--md"></runningJobCard>
    </div>
  </div>
</template>
<script>
import carInfo from '@/components/carInfo.vue'
import DonkeycarManagerService from '@/js/service.js'
import waitingJobCard from '@/components/waitingJob.vue'
import runningJobCard from '@/components/runningJobCard.vue'
import axios from 'axios'

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
      this.waitingJobs = await srv.getDrivingWaitingQueue(true, 0, 100)
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
    },
    addRecord (job) {
      const newJob = {
        player_id: job.player_id,
        state: 'WAITING',
        worker_type: 'CAR',
        name: 'RECORD',
        parameters: JSON.stringify({ drive_time: 120 }, null, 2),
        worker_id: job.worker_id,
        rank: 999
      }
      axios.post(srv.apiUrl + '/jobs', newJob).then(res => console.log(res.data))
    }
  }
}

</script>
<style>
.waitingJobCard{
  padding-top:30px;
}
.jobs-card{
  padding-top: 25px;
  display: flex;
  gap: 0.75em;
  padding: 0.5em;
  height: calc(100vh - 3.5em);
}

.running-jobs {
  flex: 1;
}

.jobs-wrap {
  display: flex;
  flex-direction: column;
  flex: 1;
  box-shadow: 0 0.3em 0.6em rgba(0,0,0,0.1);
  position: relative;
}
.jobs {
  overflow-y: scroll;
  display: flex;
  flex-direction: column;
  gap: 0.5em;
}
.jobs-over {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  pointer-events: none;
}

.header {
  height: 3.5em;
}
</style>
