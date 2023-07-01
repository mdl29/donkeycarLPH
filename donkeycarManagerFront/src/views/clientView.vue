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
import { getJobDuration, getJobWaitTime } from '@/js/utils.js'
import carView from '@/components/carView.vue'
import { io } from 'socket.io-client'

const ip = DonkeycarManagerService.ip
const url = `http://${ip}:8000`
const srv = new DonkeycarManagerService(url)
const carCount = 3
const socket = io.connect(url, { path: '/ws/socket.io' })
export default {
  components: {
    carView
  },
  data () {
    return {
      // Array of { car, job, race }
      entries: [],
      waitingList: [],
      waitTime: [],
      interval: null
    }
  },
  mounted () {
    this.fetchWaitingList()
    this.fetchCars().then(async () => {
      await that.fetchJobs()
      that.waitTime = that.waitingList.map((_, i) => that.getEstimatedWait(i))
    })
    const that = this
    this.interval = setInterval(() => {
      that.waitTime = that.waitingList.map((_, i) => that.getEstimatedWait(i))
    }, 5000)
  },
  unmounted () {
    clearInterval(this.interval)
  },
  created () {
    const that = this
    // TODO: that
    // I don't really know what event implies what change,
    // so I update jobs on every case but this could be optimized
    socket.on('car.updated', async data => {
      console.debug('clientView.event: car.updated')
      await that.fetchCars()
      that.fetchJobs()
    })
    socket.on('car.added', async data => {
      console.debug('clientView.event: car.added')
      await that.fetchCars()
      that.fetchJobs()
    })
    socket.on('laptimer.added', async data => {
      console.debug('clientView.event: laptimer.added')
      await that.fetchCars()
      that.fetchJobs()
    })
    socket.on('jobs.all.updated', async data => {
      console.debug('clientView.event: jobs.all.updated')
      that.fetchWaitingList()
      await that.fetchCars()
      that.fetchJobs()
    })
    socket.on('worker.all.updated', async data => {
      console.debug('clientView.event: worker.all.updated')
      that.fetchWaitingList()
      await that.fetchCars()
      that.fetchJobs()
    })
  },
  methods: {
    // fetch and update the cars
    async fetchCars () {
      const cars = await srv.getCars(0, 10)
      for (const car of cars) {
        const state = car.worker.state
        const index = this.entries.findIndex(e => e.car.name === car.name)

        if (state === 'BUSY' || state === 'AVAILABLE') {
          if (index >= 0) {
            this.entries[index].car = car
            this.entries[index].race = car.race
            console.debug('clientView: (update) displaying car %s', car.name)
          } else if (this.entries.length < carCount) {
            this.entries.push({ car: car, job: undefined, race: car.race })
            console.debug('clientView: (added)  displaying car %s', car.name)
          }
        } else if (state === 'STOPPED' && index >= 0) {
          this.entries.splice(index, 1)
        }
      }
      this.entries.sort((a, b) => a.car.worker_id - b.car.worker_id)
      if (this.car1) {
        this.job1 = await srv.getJobCar(this.car1.worker_id)
      }
      if (this.car2) {
        this.job2 = await srv.getJobCar(this.car2.worker_id)
      }
    },
    // fetch and update the jobs of the currently displayed cars
    async fetchJobs () {
      this.entries = await Promise.all(
        this.entries.map(async entry => {
          entry.job = (await srv.getJobCar(entry.car.worker_id))[0]
          return entry
        })
      )
    },
    async fetchWaitingList () {
      this.waitingList = await srv.getDrivingWaitingQueue(true, 0, 20)
    },
    getEstimatedWait (index) {
      const currentJobsWait = this.entries.map(e => {
        let duration = e.job ? getJobDuration(e.job) : 0
        if (e.race && e.race !== null) {
          const elapsed = new Date().getTime() - new Date(e.race.start_datetime).getTime()
          duration = Math.max(Math.floor(duration - elapsed / 1000), 0)
        }
        return Math.max(duration, 0)
      })
      const waitlist = this.waitingList.slice(0, index).map(getJobDuration)
      const previous = currentJobsWait.concat(waitlist)
      let time = getJobWaitTime(previous, this.entries.length)
      if (time === -1) {
        return ''
      } else if (time === 0) {
        return 'maintenant'
      } else if (time < 60) {
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
  max-height: 100vh;
}
.car-views {
  display:flex;
  flex-direction: row;
  flex: 1;
  max-height: calc(100% - 3.5em);
}
.car-view {
  display: flex;
  flex: 2;
  box-sizing: content-box;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
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
  background-color: white;
  padding-top: 0.4em;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
  min-height: 3.5em;
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
