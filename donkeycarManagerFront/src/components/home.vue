<template>

<div>
  <h1 class="title-header"> DONKEYCAR APP </h1>
  <div class="grid">
    <vs-row class="contents-wrapper">
      <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="12" class="description-wrapper">
        <p class="description">Les Petits Hackers de la maison du libre ont transformé des voitures radio commandées en véhicules doté d'une Intelligence Artificielle, capables de conduire tous seuls. Cependant ces voitures ont besoin d'apprendre à conduire ! As-tu l'âme d'un pilote de F1 ? Vient sur notre stand tester tes talents de pilote et comprendre le fonctionnement de ces voitures. Tu pourras conduire une voiture sur un circuit, enregistrer ta course, concevoir ton propre modèle d'IA ! </p>
        <span class="Hashtag"> <a>#IA</a> <a>#OpenSource</a>  <a>#ComputerVision</a> </span>
      </vs-col>
      <vs-col align="center" w="12">
        <vs-button warn gradient @click="active = 25; redirect()" class="register-button">S'inscrire</vs-button>
      </vs-col>
    </vs-row>
  </div>
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

.Hashtag{
  color: blue ;
  font-weight: bold;
}
.contents-wrapper{
  padding-top:100px;
}

.description-wrapper{
  padding:40px;
}

.register-button{
  font-family: 'Radio Canada', sans-serif;
  width:300px;
  height:75px;
  font-size:35px;
}
</style>
