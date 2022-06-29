<template>
  <div class="client-view">
    <div class="car-views">
      <template v-if="entries.length > 0">
        <div class="car-view" v-for="entry in entries" :key="entry.car.name">
          <car-view :car="entry.car" :job="entry.job" :race="entry.race" />
        </div>
      </template>
      <div v-else class="no-cars">
        Aucune voiture en marche
      </div>
    </div>
    <div class="waiting-list" v-if="waitingList.length > 0">
      <div v-for="(job, index) in waitingList" :key="job.job_id" class="waiting-list-item">
        <div class="name">{{ job.player.player_pseudo }}</div>
        <div class="wait">{{ waitTime[index] || "" }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import DonkeycarManagerService from '@/js/service.js'
import carView from '@/components/carView.vue'
import { io } from 'socket.io-client'

const ip = 'localhost'
const url = `http://${ip}:8000`
const srv = new DonkeycarManagerService(url)
const car_count = 2
const socket = io.connect(url, { path: `/ws/socket.io` })

export default {
  components: {
    carView,
  },
  data() {
    return {
      // Array of { car, job, race }
      entries: [],
      waitingList: [],
      waitTime: [],
      interval: null,
    }
  },
  mounted() {
    this.fetchWaitingList()
    this.fetchCars().then(async () => {
      await Promise.all([
        that.fetchJobs(),
        that.fetchRaces(),
      ])
      that.waitTime = that.waitingList.map((_, i) => that.getEstimatedWait(i))
    })
    const that = this
    this.interval = setInterval(() => {
      that.waitTime = that.waitingList.map((_, i) => that.getEstimatedWait(i))
    }, 5000)
  },
  unmounted() {
    clearInterval(this.interval)
  },
  created() {
    const that = this
    // TODO: that
    // I don't really know what event implies what change,
    // so I update jobs on every case but this could be optimized
    socket.on('car.updated', async data => {
      console.debug('clientView.event: car.updated')
      await that.fetchCars()
      that.fetchJobs()
      that.fetchRaces()
    })
    socket.on('car.added', async data => {
      console.debug('clientView.event: car.added')
      await that.fetchCars()
      that.fetchJobs()
      that.fetchRaces()
    })
    socket.on('laptimer.added', async data => {
      console.debug('clientView.event: laptimer.added')
      await that.fetchCars()
      that.fetchJobs()
      that.fetchRaces()
    })
    socket.on('jobs.all.updated', async data => {
      console.debug('clientView.event: jobs.all.updated')
      that.fetchWaitingList()
      await that.fetchCars()
      that.fetchJobs()
      that.fetchRaces()
    })
    socket.on('worker.all.updated', async data => {
      console.debug('clientView.event: worker.all.updated')
      that.fetchWaitingList()
      await that.fetchCars()
      that.fetchJobs()
      that.fetchRaces()
    })
  },
  methods: {
    // fetch and update the cars
    async fetchCars() {
      const cars = await srv.getCars(0, 10)
      for (const car of cars) {
        const state = car.worker.state
        const index = this.entries.findIndex(e => e.car.name === car.name)

        if(state === 'BUSY' || state === 'AVAILABLE') {
          if (index >= 0) {
            this.entries[index].car = car
            console.debug('clientView: (update) displaying car %s', car.name)
          } else if (this.entries.length < car_count) {
            this.entries.push({ car: car, job: undefined, race: undefined })
            console.debug('clientView: (added)  displaying car %s', car.name)
          }
        } else if (state === 'STOPPED' && index >= 0) {
          this.entries.splice(index, 1)
        }
      }
      if (this.car1){
        this.job1 = await  srv.getJobCar(this.car1.worker_id)
      }
      if (this.car2){
        this.job2 = await  srv.getJobCar(this.car2.worker_id)
      }
    },
    // fetch and update the jobs of the currently displayed cars
    async fetchJobs() {
      this.entries = await Promise.all(
        this.entries.map(async entry => {
          entry.job = (await srv.getJobCar(entry.car.worker_id))[0]
          return entry
        })
      )
    },
    // fetch and update the races of the currently displayed cars
    async fetchRaces() {
      const races = await srv.fetchRaces(0, 10)
      for (const entry of this.entries) {
        entry.race = races.find(r => r.player_id === entry.car.player.player_id)
      }
    },
    async fetchWaitingList() {
      this.waitingList = await srv.getDrivingWaitingQueue(true, 0, 20)
    },
    getJobDuration(job) { // in seconds
      try {
        return parseInt(JSON.parse(job.parameters).drive_time)
      } catch(_) {
        return 0
      }
    },
    getEstimatedWait(index) {
      // I want spread operator
      const that = this
      const current_jobs_wait = this.entries.filter(e => e.job).map(e => {
        let duration = that.getJobDuration(e.job);
        if (e.race && e.race !== null) {
          const elapsed = new Date().getTime() - new Date(e.race.start_datetime).getTime();
          duration = Math.max(Math.floor(duration - elapsed / 1000), 0)
        }
        return duration
      })
      const min_current_job_wait = current_jobs_wait.length > 0 ? Math.min.apply(Math, current_jobs_wait) : 0
      const waitingTimes = this.waitingList.filter((_, i) => i < index).map(this.getJobDuration)
      let time = 0;
      if (waitingTimes.length > 0) {
        time = min_current_job_wait + waitingTimes.reduce((acc, v) => acc + v, 0)
      } else {
        time = min_current_job_wait
      }
      if (time < 60) {
        return `${time}s`
      } else {
        time = Math.round(time / 60)
        return `${time} min`
      }
    }
  }
}
</script>

<style scoped>
.client-view {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
}
.car-views {
  display:flex;
  flex-direction: row;
  flex: 1;
}
.car-view {
  display: flex;
  flex: 2;
  box-sizing: content-box;
  flex-direction: column;
}
.car-view:not(:last-child) {
  border-right: 4px dashed gray;
}
.waiting-list {
  display: flex;
  flex-direction: row;
  overflow-x: hidden;
  padding-bottom: 0.4em;
  padding-left: 0.4em;
  z-index: 20;
  background-color: white;
  padding-top: 0.4em;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
}
.waiting-list::after {
  display: block;
  content: "";
  height: 2.8em;
  position: absolute;
  right: 0;
  width: 6em;
  background: linear-gradient(to right, transparent, white 150%)
}
.waiting-list-item {
  background-color: #4287f5;
  border-radius: 2em;
  padding: 0.8em;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  color: white;
  margin-right: 0.5em;
  flex-shrink: 0;
}
.waiting-list-item .name {
  margin-right: 0.5em;
  font-weight: bold;
}
.no-cars {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 4em;
  font-weight: bold;
}
</style>
