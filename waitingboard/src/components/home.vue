<template>

<div>
  <h1 class="title-header"> DONKEYCAR APP </h1>
  <vs-row class="contents-wrapper" align="center" justify="space-around" direction="column">
    <vs-col w="5" class="description-wrapper">
      <p class="description">Logoden biniou degemer mat, an. Poan tamm ha pemzek, stal. Gwele vourc’h ur gaer, krib. Seiz gounit warno abred, Entraven. Kalet poultrenn start ennout, Groe. Bemnoz danvez c'hanon gourc’hemennoù, da. Sailh kasoni galon Egineg, degouezhout. Da doñv ifern estreget , araok. Bluenn tre urzh digwener, Pont-Aven. Egile Kernev all Roazhon, sadorn.</p>
    </vs-col>
    <vs-col w="2">
      <vs-button warn gradient @click="active = 25; redirect()" class="register-button">S'inscrire</vs-button>
    </vs-col>
  </vs-row>
</div>
</template>

<script>
export default {
  methods: {
    redirect () {
      this.$router.push('/register')
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather+Sans:wght@700&family=Radio+Canada:wght@500&display=swap');

.contents-wrapper{
  padding-top:100px;
}

.description-wrapper{
  padding:40px;
}

.register-button{
  position: relative;
  font-family: 'Radio Canada', sans-serif;
  width:300px;
  height:75px;
  font-size:35px;
}
</style>
