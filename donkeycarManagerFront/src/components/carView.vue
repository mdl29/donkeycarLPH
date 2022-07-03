<template>
  <div class="car">
    <div class="header" :class="{blur: is_paused}"> 
      <div class="record" v-if="job && (job.name === 'RECORD' || job.name === 'AUTO')">
        {{ job.name === 'RECORD' ? "REC" : "AUTO" }}
      </div>
      <div class="username" v-if="job">{{ job.player.player_pseudo }}</div>
      <div :class="{name_job: job, name: !job}" :style="{'--color': color}">{{ car.name }}</div>
    </div>
    <div class="content" :class="{blur: is_paused}">
      <div v-if="job" class="job">
        <div v-if="race" class="race">
          <!-- head -->
          <div class="lap head" v-if="race.laptimers.length > 0 || timeleft > 0">
            <div class="number"> Tour </div>
            <div class="duration"> Temps </div>
          </div>
          <!-- laptimers -->
          <transition-group :duration="200" appear
            @before-enter="onBeforeEnter"
            @enter="onEnter"
            @after-enter="onAfterEnter"
            @before-leave="onBeforeLeave"
            @leave="onLeave"
            @after-leave="onAfterLeave"
            >
            <div 
              v-for="lap in laptimers"
              class="lap"
              :class="{ 
                best: isBestLap(lap),
                ongoing: lap.current,
                real: !lap.current
              }"
              :key="lap.laptimer_id"
            >
              <div class="number">{{ lap.index + 1 }}</div>
              <div class="duration">
                {{
                  lap.current
                    ? formatMMs(currentlapDuration)
                    : formatMMs(lap.duration)
                }}
              </div>
            </div>
          </transition-group>
        </div>
        <div v-if="race && timeleft > 0" class="end">
          Finit dans <strong>{{ formatM(timeleft) }}</strong>
        </div>
        <div v-if="job && job.screen_msg_display" class="end message">
          <template v-for="part in messageComponents">
            <span v-if="part.text">
              {{ part.text }}
            </span>
            <textIcon :src="part.img" v-if="part.img" />
          </template>
        </div>
        <div v-if="!race" class="no-race"> Veuillez avancer pour lancer la course </div>
      </div>
      <waiting-text v-else />
    </div>
  </div>
</template>

<script>
import waitingText from '@/components/waitingText.vue'
import textIcon from '@/components/textIcon.vue'

export default {
  components: {
    waitingText,
    textIcon,
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
        that.timeleft = (that.race.max_duration * 1000) - that.fromNow(that.race.start_datetime)
        const start = that.race.laptimers.length > 0
          ? that.race.laptimers[that.race.laptimers.length - 1].end_datetime
          : that.race.start_datetime
        that.currentlapDuration = that.fromNow(start)
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
      const height = (a) => {
        const e = document.querySelector(a)
        return e ? e.offsetHeight : 0
      }
      const lap = Array.from(document.querySelectorAll(".lap.real"))
        .map(v => v.offsetHeight)
        .reduce((a, b) => Math.max(a, b), 0)
      if (lap != 0) {
        let availableHeight = height(".job")
        availableHeight -= height(".lap.ongoing")
        availableHeight -= height(".lap.head") // remove height of head
        availableHeight -= height(".header") // remove height of header
        availableHeight -= height(".end")
        availableHeight *= 0.6 // remove some space to leave gaps
        const maxTimers = Math.max(Math.floor(availableHeight / lap), 1)
        if (this.maxTimers != maxTimers) {
          this.maxTimers = maxTimers
          console.debug("displaying %i laps", this.maxTimers + 1)
        }
      }
    },
    bestLapIndex() {
      let d = Infinity
      let i = -1
      this.race.laptimers.forEach((v, index) => {
        if (v.duration < d) i = index
        d = Math.min(v.duration, d)
      })
      return i
    },
    isBestLap(lap) {
      if (this.race) {
        const max = this.race.laptimers.map(v => v.duration).reduce((a, b) => Math.min(a, b), Infinity)
        return max === lap.duration
      } else {
        return false
      }
    },
    // because it doesn't fucking work otherwise
    onBeforeEnter(el) {
      el.classList.add("list-enter", "list-enter-active")
      requestAnimationFrame(() => {
        el.classList.replace("list-enter", "list-enter-to")
      });
    },
    // We should be able to just use that, but doesn't work consistently so ¯\_(ツ)_/¯
    onEnter(el) {},
    // because I need js for one thing, i'm using hooks for all the classes
    onAfterEnter(el) {
      el.classList.remove("list-enter-to", "list-enter-active")
    },
    onBeforeLeave(el) {
      el.classList.add("list-leave", "list-leave-active")
    },
    onLeave(el) {
      el.classList.replace("list-leave", "list-leave-to")
    },
    onAfterLeave(el) {
      el.classList.remove("list-leave-to", "list-leave-active")
    },
  },
  computed: {
    color() {
      return `#${this.car.color}`
    },
    messageComponents() {
      if (this.job && this.job.screen_msg) {
        const str = this.job.screen_msg
        const groups = str.split(/[\]\[]/g);
        const res = []
        let type = "text"
        for (const m of groups) {
          if (type === "text") {
            res.push({text: m})
            type = "img"
          } else {
            res.push({img: `PS4_${m}.png`})
            type = "text"
          }
        }
        return res
      }
    },
    is_paused() {
      return this.job && this.job.state == 'PAUSED'
    },
    laptimers() {
      const offset = Math.max(this.race.laptimers.length - this.maxTimers, 0)
      const a = this.race.laptimers.slice(-this.maxTimers).map((v, i) => {
        v.index = offset + i
        return v
      })
      if (a.length > 0) {
        const bestIndex = this.bestLapIndex()
        if (bestIndex < offset) {
          a[0] = this.race.laptimers[bestIndex]
          a[0].index = bestIndex
        }
      }
      if (this.timeleft > 0) {
        a.push({
          duration: NaN,
          laptimer_id: 9999999999,
          current: true,
          index: this.race.laptimers.length
        })
      }
      return a
    },
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
  transition: all 0.2s ease;
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
  transition: all 0.2s ease;
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
.header.blur .username {
  color: white;
}
.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 2;
  justify-content: space-evenly;
  margin-top: -4.6em;
  overflow-y: hidden;
  transition: all 0.2s ease;
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
  filter: blur(0.5em);
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
}
.lap {
  display: flex;
  flex-direction: row;
  gap: 1em;
  justify-content: center;
  padding-top: 0.3em;
}
.lap .number {
  width: 3.6rem;
  text-align: start;
  padding-left: 0.9rem;
}
.lap::before {
  content: "";
  display: block;
  width: 1.8em;
  height: 1.1em;
  margin-right: -1.1em;
  margin-left: 0.3em;
}
.lap.best::before {
  content: "";
  display: block;
  background-image: url("../assets/crown.png");
  background-size: cover;
  background-position: center;
  margin-right: -1.1em;
  margin-left: 0.3em;
  width: 1.8em;
  height: 1.1em;
}
.lap.best {
  color: #FAD000;
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
.message {
  font-size: 2em;
}
.record {
  font-size: 1em;
  font-weight: bold;
  padding: 0.4em;
  padding-bottom: 0.2em;
  border: 3px solid black;
  border-radius: 2em;
  color: black;
  margin-right: 1em;
}
.record::before {
  content: "⬤ ";
  padding-bottom: 0.2em;
  font-size: 0.8em;
  color: red;
  animation: blink infinite normal running 1s steps(1, start);
}
@keyframes blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}
/* why is that necessary for animation ?? */
.lap {
  max-height: 2em;
}

.list-enter-to,
.list-leave {
  max-height: 2em;
  opacity: 1;
}

.list-enter,
.list-leave-to {
  max-height: 0em;
  opacity: 0;
}

.list-move,
.list-leave-active,
.list-enter-active {
  overflow-y: hidden;
  border-color: transparent;
  transition-duration: 0.2s;
}

.list-move {
  transition-timing-function: linear;
}
.list-leave-active {
  transition-timing-function: ease-out;
}
.list-enter-active {
  transition-timing-function: ease-in;
}

.lap.real.list-enter,
.lap.real.list-leave-to {
  border-color: transparent;
  padding: 0;
}
</style>
