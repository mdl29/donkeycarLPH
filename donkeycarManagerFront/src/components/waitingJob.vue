<template>
  <va-card class="jobCard">
        <va-card-content class="job-content">
          <div class="card-main-info">
            <div class="pseudo">{{job.player.player_pseudo}}</div>
            <div class="id"> {{job.job_id}}</div>
            <div class="spacer"></div>
            <div class="type"> {{job.worker_type}}</div>
          </div>
          <div>
            <va-button @click="this.$emit('go1', this.job)"  color="#ffec33" class="mr-4 mb-2"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-zap"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg></va-button>
            <va-button @click="this.$emit('goUp', this.job)" color="#9FB4FF" class="mr-4 mb-2"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2c5.52 0 10 4.48 10 10s-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2zm0 18c4.42 0 8-3.58 8-8s-3.58-8-8-8-8 3.58-8 8 3.58 8 8 8zm1-8v4h-2v-4H8l4-4 4 4h-3z"/></svg></va-button>
            <va-button @click="this.$emit('goDown', this.job)" color="#9FB4FF" class="mr-4 mb-2"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M12 2c5.52 0 10 4.48 10 10s-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2zm0 18c4.42 0 8-3.58 8-8s-3.58-8-8-8-8 3.58-8 8 3.58 8 8 8zm1-8h3l-4 4-4-4h3V8h2v4z"/></svg></va-button>
            <va-button @click="this.$emit('remove', this.job)"  color="danger" class="mr-4 mb-2"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24"><path fill="none" d="M0 0h24v24H0z"/><path d="M17 6h5v2h-2v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V8H2V6h5V3a1 1 0 0 1 1-1h8a1 1 0 0 1 1 1v3zm1 2H6v12h12V8zm-9 3h2v6H9v-6zm4 0h2v6h-2v-6zM9 4v2h6V4H9z"/></svg></va-button>
          </div>
          <div class="row align-self--start">
            <va-badge text="waiting" color="warning"/>
          </div>
        </va-card-content>
      </va-card>
</template>

<script>

export default {
  props: {
    job: Object

  },
  methods: {
    async goUp () {
      this.$emit('goUp', this.job)
    }
  }
}
</script>
<style scoped>
.card-main-info{
  font-size: 20px;
  width: 100%;
  display: flex;
  padding-bottom: 20px;
}

.pseudo {
  font-weight: bold;
}

.id::before {
  color: grey;
  content: "#"
}

.id {
  color: grey;
  margin-left: 0.5em;
}

.spacer {
  flex: 2;
}
</style>
