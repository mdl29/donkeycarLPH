<template>
  <div>
    <h1 class="title-header"> Devenir pilote en accédant à la liste d'attente </h1>
    <div class="inputs-wrapper">
      <vs-row align="center" justify="center">
          <vs-input class="input" color="#7d33ff" shadow border type="text"  v-model="pseudo" label-placeholder="Pseudo" style="padding:20px" required="required">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" style="fill: rgba(84, 83, 83, 1);transform: ;msFilter:;"><path d="M12 2a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm0 8a3 3 0 1 1 3-3 3 3 0 0 1-3 3zm9 11v-1a7 7 0 0 0-7-7h-4a7 7 0 0 0-7 7v1h2v-1a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v1z"></path></svg>
            </template>
            <template v-if="pseudoBlank == true " #message-danger>
              veuillez choisir un pseudo
            </template>
          </vs-input>
      </vs-row>
      <vs-row>
        <vs-col  align="center" justify="center" w="12">
          <vs-button class="submit-btn" circle color="warn" gradient @click="check()"> S'enregistrer </vs-button>
        </vs-col>
      </vs-row>
    </div>
    <vs-dialog width="550px" prevent-close blur not-close v-model="popup">
      <template #header>
        <h2 class="not-margin"> Bienvenue <b>{{pseudo}}</b></h2>
      </template>
      <div class="con-content">
        <p>Vous venez d'être enregistré(e) !!</p>
        <h3> Votre pseudo : {{player.player_pseudo}} </h3>
        <h3> Votre numéro : {{numero}} </h3>
        <h3> temps d'attente : {{attente}} min </h3>
      </div>
      <template #footer>
        <div class="con-footer">
          <vs-button @click="popup=false ; redirect() " >Ok</vs-button>
        </div>
      </template>
    </vs-dialog>
  </div>
</template>

<script>

import DonkeycarManagerService from '@/js/service.js'

const ip = 'localhost'
const srv = new DonkeycarManagerService('http://' + ip + ':8000')

export default {
  data: () => ({
    pseudo: '',
    player: [],
    popup: false,
    pseudoBlank: false,
    telBlank: false,
    numero: 0,
    attente: 0
  }),
  methods: {
    check () {
      if (this.pseudo === '') {
        this.pseudoBlank = true
      } else {
        this.addUser()
      }
    },
    redirect () {
      this.$router.push('/')
    },
    async addUser () {
      const drivingWaitingQueue = await srv.getDrivingWaitingQueue(true, 0, 20)
      const allCars = await srv.getCars(0, 5)
      let nbrpPlayers = drivingWaitingQueue.length / allCars.length
      this.attente = nbrpPlayers * 15
      console.log(drivingWaitingQueue.length)
      console.log(this.attente)
      this.player = await srv.createPlayer(this.pseudo)
      await srv.addDrivingWaitingQueue(this.player.player_id)
      this.numero = this.player.player_id
      this.popup = true
    }
  }
}
</script>
<style>
.submit-btn{
  font-size:20px;
  font-weight: bold;
  height:50px;
  width:170px;
}
.inputs-wrapper{
    padding:50px;
    height: 60px;
}
</style>
