<template>
    <va-card class="job-card">
          <va-card-content class="job-content">
            <div class="row justify--space-between">
              <va-badge :color="carColor" :text="carName" />
              <p id="text-info"> <b>{{job.player.player_pseudo}}</b></p>
            </div>
            <div>
              <!-- Resume button-->
              <va-button color="success" class="mr-4 mb-2 play" v-if="job.state === 'PAUSED'" ><img src="../assets/icons/play.svg" @click="this.$emit('resume', this.job)"></va-button>
              <va-button loading size="small" color="success" class="mr-4 mb-2 play" v-if="job.state === 'RESUMING'" ><img src="../assets/icons/play.svg"></va-button>
              <!-- Reload button-->
              <va-button color="warning" class="mr-4 mb-2 play" v-if="job.state === RUNNING" ><img src="../assets/icons/recordIcon.svg" @click="this.$emit('record', this.job)"></va-button>
              <va-button loading size="small" color="warning" class="mr-4 mb-2 play" v-if="job.state !== RUNNING || job.state === PAUSED " ><img src="../assets/icons/reload.svg"></va-button>
              <!-- Reload button-->
              <va-button color="#9370DB" class="mr-4 mb-2 play" v-if="reload === false" ><img src="../assets/icons/recordIcon.svg" @click="this.$emit('reload', this.job)"></va-button>
              <va-button loading size="small" color="#9370DB" class="mr-4 mb-2 play" v-if="reload === true" ><img src="../assets/icons/reload.svg"></va-button>
              <!-- Cancel button-->
              <va-button color="#FF4C4C" class="mr-4 mb-2 play" v-if="job.state !== 'CANCELLING'" ><img src="../assets/icons/cancel.svg" @click="this.$emit('reload', this.job)"></va-button>
              <va-button loading size="small" color="#FF4C4C" class="mr-4 mb-2 play" v-if="job.state === 'CANCELLING'" ><img src="../assets/icons/cancel.svg"></va-button>
            </div>
            <div class="row align-self--start">
              <!-- Status badges-->
              <va-badge color="#00b4d8" text="🎮 Drive" v-if="job.state === 'RUNNING'" class="mr-4" />
              <va-badge color="warning" text="⏸ Pausing" v-if="job.state === 'PAUSING'" class="mr-4" />
              <va-badge loading color="info" text="▶️ Resuming" v-if="job.state === 'RESUMING'" />
              <va-badge loading color="danger" text="Cancelling" v-if="job.state === 'CANCELLING'" />
              <va-badge color="warning" text="⏸ Pause" v-if="job.state === 'PAUSED'" />
              <!-- Management buttons-->
            </div>
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
</style>
