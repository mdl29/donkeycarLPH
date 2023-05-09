<template>
  <div class="carCard">
    <va-card  class="car-card" stripe :stripe-color="'#'+car.color" >
        <va-card-title><b>{{ car.name }}</b></va-card-title>
        <va-card-content class="content-card ">
          <b>Ip :</b> {{car.ip}} <br>
          <b> Status:</b>
          <va-badge v-if="car.current_stage === 'DRIVE'" text="🎮 Drive" color="warning" class="mr-4" />
          <va-badge v-if="car.current_stage === 'RECORD'" text="🎥 recording data" color="#8338ec" class="mr-4" />
          <va-badge v-if="car.current_stage === 'AI_ASSISTED'" text="🧪 AI assisted" color="#06d6a0" class="mr-4" />
          <va-badge v-if="car.current_stage === 'MAINTENANCE'" text="🧰 Maintenance" color="fe5f55" class="mr-4" />
          <va-badge v-if="!car.current_stage" text="❌ no status" color="#fe5f55" class="mr-4" />
          <p v-if="car.current_player_id"><b> used by :</b> {{car.player.player_pseudo}}</p>
          <p v-if="!car.current_player_id"><b> used by :</b> nobody</p>
          <p v-if="car.worker"><b> state :</b> {{ car.worker.state }}</p>
        </va-card-content>
    </va-card>
  </div>
</template>

<script>
export default {
  props: {
    car: Object
  }
}
</script>
<style scoped>
.car-card .content-card{
  text-align: left ;
}
.carCard {
  transition: transform .5s;
}
.carCard:hover {
  transform: scale(1.05);
}
</style>
