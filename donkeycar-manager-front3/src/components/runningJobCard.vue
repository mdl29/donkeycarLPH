<template>
    <va-card class="job-card">
          <va-card-content class="job-content">
              <va-badge :color="carColor" :text="carName" />
              <p id="text-info"> <b>{{job.player.player_pseudo}}</b></p>
              <!-- Status badges-->
              <va-badge color="#00b4d8" text="🎮 Drive" v-if="job.state === 'RUNNING'" class="mr-4" />
              <va-badge color="warning" text="⏸ Pausing" v-if="job.state === 'PAUSING'" class="mr-4" />
              <va-badge loading color="info" text="▶️ Resuming" v-if="job.state === 'RESUMING'" />
              <va-badge loading color="danger" text="🚫 Cancelling" v-if="job.state === 'CANCELLING'" />
              <va-badge color="warning" text="⏸ Pause" v-if="job.state === 'PAUSED'" />
              <!-- Management buttons-->
              <!-- Resume button-->
              <va-button color="success" class="mr-4 mb-2 play" v-if="job.state === 'PAUSED'" ><img src="../assets/icons/play.svg" @click="this.$emit('resume', this.job)"></va-button>
              <va-button loading size="small" color="success" class="mr-4 mb-2 play" v-if="job.state === 'RESUMING'" ><img src="../assets/icons/play.svg"></va-button>
              <!-- Reload button-->
              <va-button color="warning" class="mr-4 mb-2 play" v-if="reload === false" ><img src="../assets/icons/reload.svg" @click="this.$emit('reload', this.job)"></va-button>
              <va-button loading size="small" color="warning" class="mr-4 mb-2 play" v-if="reload === true" ><img src="../assets/icons/reload.svg"></va-button>
              <!-- Cancel button-->
              <va-button color="#FF4C4C" class="mr-4 mb-2 play" v-if="job.state !== 'CANCELLING'" ><img src="../assets/icons/cancel.svg" @click="this.$emit('reload', this.job)"></va-button>
              <va-button loading size="small" color="#FF4C4C" class="mr-4 mb-2 play" v-if="job.state === 'CANCELLING'" ><img src="../assets/icons/cancel.svg"></va-button>

          </va-card-content>
        </va-card>
  </template>

<script>
export default {
  props: {
    job: { type: Object },
    carColor: { type: String },
    carName: { type: String },
    reload: { type: Boolean }
  }
}
</script>
<style scoped>
#text-info{
  font-size: 20px;
  padding-left: 2;
  padding-bottom: 25px;
}
.job-card{
  border-radius: 25px;
}
.job-info{
  display: inline-flex;
}
.content{
  padding-left: 30px;
}
.play{
  border: none;
  width: 32px;
  height: 32px;
  background-color: #eee;
  transition: all ease-in-out 0.2s;
  cursor: pointer;
}
.play:hover{
  border: 1px solid #888;
  background-color: #ddd;
}
</style>
