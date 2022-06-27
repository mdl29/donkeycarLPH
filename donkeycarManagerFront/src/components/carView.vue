<template>
  <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="6" class="pilot-wrapper" >
  <div v-if="car === null || job[0] === undefined">
    <!-- No player assigned, display waiting message -->
    <h1> Player {{ number }}</h1>
    <waiting-text />
  </div>
  <div v-if="car !== null" class="melanchon">
    <div v-if="car.race">
        <vs-button  size="xl" :color="'#'+car.color" class="car-name-button"> {{car.name}}</vs-button>
        <template v-if="job[0].player.player_pseudo !== undefined">
          <h1> {{ job[0].player.player_pseudo}} </h1>
          <h1> Unknow player </h1>
        </template>
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
                <vs-tr v-for="(lap, i) in car.race.laptimers" v-bind:key="lap.laptimer_id">
                    <vs-td>
                        {{i+1}}
                    </vs-td>
                    <vs-td>
                        {{lap.duration/1000}} s
                    </vs-td>
                </vs-tr>
                </template>
            </vs-table>
            <h4 v-if="car.race.laptimers.length > 0" class="best-score-text">
              Meilleur temps : {{getBestScore(car.race.laptimers)}}s
            </h4>
        </div>
          <div class="video-wrapper">
          <img id='mpeg-image' class='img-responsive' :src="'http://'+ car.ip + ':8887/video'"/>
        </div>
    </div>
    <div v-else>
        <vs-button  size="xl" :color="'#'+car.color" class="car-name-button"> {{car.name}}</vs-button>
        <template v-if="job[0]">
          <h1 v-if="job[0].player.player_pseudo !== undefined">
            {{ job[0].player.player_pseudo}}
          </h1>
          <h1 v-if="job[0].player.player_pseudo === undefined">
            Unknow player
          </h1>
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
</template>

<script>
// Unecessarily fancy text displaying 'Waiting...'
import waitingText from './waitingText.vue'

export default {
  components: {
    waitingText,
  },
  props: ["car", "job", "number"],
  methods: {
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

<style scoped>
.no-laptimer-text{
  margin-top: 10%;
  font-size: 25px;
  animation: grow-animation 1s linear infinite;
}

.best-score-text{
 font-size: 15px;
 animation: grow-animation 1s linear infinite;
}

.table-head{
  text-align: left !important;
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

.pilot-wrapper {
  border-right: 2.5px dashed grey;
  flex-grow: 2;
  height: 100%;
  flex-direction: column;
  justify-content: center;
  justify-items: center;
  align-items: center;
}
.melanchon {
  height: 100%;
  display: flex;
  justify-content: center;
  flex-direction: column;
}
</style>
