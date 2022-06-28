<template>
  <div class="car">
    <div class="header" :class="{blur: is_paused}"> 
      <div class="username" v-if="job">{{ job.player.player_pseudo }}</div>
      <div :class="{name_job: job, name: !job}" :style="{'--color': color}">{{ car.name }}</div>
    </div>
    <div class="content" :class="{blur: is_paused}">
      <div v-if="job" class="job">
        <div v-if="race" class="race">
          <!-- head -->
          <div class="lap head">
            <div class="number"> Tour </div>
            <div class="duration"> Temps </div>
          </div>
          <!-- laptimers -->
          <div v-for="(lap, index) in laptimers" class="lap real">
            <div class="number">{{ index + laptimersOffset + 1 }}</div>
            <div class="duration">{{ formatMMs(lap.duration) }}</div>
          </div>
          <!-- ongoing lap -->
          <div class="lap">
            <div class="number">{{ race.laptimers.length + 1 }}</div>
            <div class="duration">{{ formatMMs(currentlapDuration) }}</div>
          </div>
        </div>
        <div v-if="race" class="end">
          Finit dans <strong>{{ formatM(timeleft) }}</strong>
        </div>
        <div v-else class="no-race"> Veuillez avancer pour lancer la course </div>
      </div>
      <waiting-text v-else />
    </div>
  </div>
</template>

<script>
import waitingText from '@/components/waitingText.vue'

export default {
  components: {
    waitingText
  },
  data() {
    return {
      currentlapDuration: 0,
      timeleft: 0,
      interval: undefined,
      maxTimers: 6
    }
  },
  mounted() {
    const that = this
    // kindof a hack, because updateMaxTimers doesn't do anything if there is no lap element in the dom 
    // which there isn't at mount
    setTimeout(() => {
      that.updateMaxTimers()
    }, 500)
    window.addEventListener("resize", () => {
      that.updateMaxTimers()
    })
    
    this.interval = setInterval(() => {
      if (that.race) {
        const start = that.race.laptimers.length > 0
          ? that.race.laptimers[that.race.laptimers.length - 1].end_datetime
          : that.race.start_datetime
        that.currentlapDuration = that.fromNow(start)
        that.timeleft = (that.race.max_duration * 1000) - that.fromNow(that.race.start_datetime)
      }
    }, 30)
  },
  unmounted() {
    clearInterval(this.interval)
  },
  props: ["car", "job", "race"],
  methods: {
    // format milliseconds timestamp -> Mmin Ss
    formatM(m) {
      m = Math.abs(m)
      if (m < 60000) {
        return `${Math.round(m / 1000)}s`
      } else {
        return `${Math.floor(m / 60000)} min ${Math.round(m / 1000) % 60}s`
      }
    },
    // format milliseconds timestamp -> SS.XX
    formatMs(m) {
      m = Math.abs(m)
      const seconds = `${Math.floor(m / 1000)}`
      const cents = `${Math.round(m/10 % 100)}`.padStart(2, "0")
      return `${seconds},${cents}`
    },
    // format milliseconds timestamp -> MM:SS.XX
    formatMMs(m) {
      const minutes = Math.floor(m / 60000)
      const seconds = `${Math.floor(m / 1000 % 60)}`.padStart(2, "0")
      const cents = `${Math.round(m/10) % 100}`.padStart(2, "0")
      return `${minutes}:${seconds},${cents}`
    },
    fromNow(ts) {
      return new Date().getTime() - new Date(ts).getTime()
    },
    updateMaxTimers() {
      const height = (a) => document.querySelector(a).offsetHeight
      const lap = document.querySelector(".lap.real")
      if (lap) {
        const lapHeight = lap.offsetHeight
        let availableHeight = height(".job")
        availableHeight -= lapHeight // remove height of ongoing lap
        availableHeight -= height(".lap.head") // remove height of head
        availableHeight -= height(".header") // remove height of header
        availableHeight -= height(".end")
        availableHeight *= 0.6 // remove some space to leave gaps
        this.maxTimers = Math.max(Math.floor(availableHeight / lapHeight), 1)
        console.debug("displaying %i laps", this.maxTimers + 1)
      }
    }
  },
  computed: {
    color() {
      return `#${this.car.color}`
    },
    is_paused() {
      return this.job && this.job.state == 'PAUSED'
    },
    laptimers() {
      return this.race.laptimers.slice(-this.maxTimers)
    },
    laptimersOffset() {
      return Math.max(this.race.laptimers.length - this.maxTimers, 0)
    }
  }
}
</script>

<style scoped>
/* font for timer */
@font-face {
  font-family: 'Azeret Mono';
  font-style: normal;
  font-weight: 400;
  src: url("../fonts/AzeretMono-VariableFont_wght.ttf") format('truetype');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
.car {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.header {
  padding-top: 1em;
  padding-bottom: 1em;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  z-index: 20;
}
.name {
  background-color: transparent;
  color: var(--color);
  font-size: 2em;
  font-weight: bold;
}
.name_job {
  display: flex;
  align-items: center;
  font-weight: bold;
  z-index: 10;
  color: white;
  background-color: var(--color);
  padding: 0.3em;
  border-radius: 5px;
}
.job {
  display: flex;
  flex: 1;
  width: 100%;
  flex-direction: column;
  justify-content: center;
}
.username {
  font-size: 2em;
  z-index: 10;
  margin-right: 0.5em;
  font-weight: bold;
}
.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 2;
  justify-content: space-evenly;
  margin-top: -4.6em;
  overflow-y: hidden;
}
.content.blur {
  background-color: rgba(0, 0, 0, 0.5);
}
.header.blur {
  background: none;
}
.content.blur::after {
  content: "Tache en pause";
  color: white;
  font-size: 3em;
  display: block;
  position: absolute;
  font-weight: bold;
}
.content.blur .job {
  filter: blur(0.3em);
}
.no-race {
  font-size: 2em;
}
.race {
  font-size: 1.8em;
  padding: 1em;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3em;
}
.lap {
  display: flex;
  flex-direction: row;
  gap: 1em;
  justify-content: center;
}
.lap .number {
  width: 3.6rem;
  text-align: start;
  padding-left: 0.9rem;
}
.lap:not(:last-child) {
  padding-bottom: 0.3em;
  border-bottom: 1px solid gray;
}
.lap .duration {
  font-family: 'Azeret Mono';
  width: 9rem;
}
.lap.head div {
  font-family: inherit;
  font-weight: bold;
  font-size: 0.8em;
  padding-left: 0.4rem;
}
.end {
 font-size: 1.2em;
}
</style>
