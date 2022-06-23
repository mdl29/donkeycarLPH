<template>
  <div>
    <h1 class="title-header"> Devenir pilote en accédant à la liste d'attente </h1>
    <div class="inputs-wrapper">
      <vs-row align="center" justify="center">
        <input type="text" placeholder="Entrez votre pseudo" id="input-form" required="required" v-model="pseudo">
      </vs-row>
      <vs-row>
        <vs-col style="padding-top: 70px;" align="center" justify="center" w="12">
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
        <h3> temps d'attente : {{attente}}</h3>
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
    attente: '',
    waitingList: []
  }),
  created () {
    const that = this
    that.fetchDrivingQueue()
  },
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
      this.player = await srv.createPlayer(this.pseudo)
      await srv.addJobs(this.player.player_id)
      if (this.waitingList.length < 2) {
        this.attente = 'Maintenant'
      } else if (this.waitingList.length >= 2 && this.waitingList.length < 4) {
        this.attente = '15 minutes'
      } else if (this.waitingList.length >= 4 && this.waitingList.length < 8) {
        this.attente = '30 minutes'
      } else if (this.waitingList.length >= 8 && this.waitingList.length < 12) {
        this.attente = '45 minutes'
      } else if (this.waitingList.length >= 12) {
        this.attente = 'plus de 1 heure'
      }
      this.numero = this.player.player_id
      this.popup = true
    },
    async fetchDrivingQueue () {
      this.waitingList = await srv.getDrivingWaitingQueue(true, 0, 20)
    }
  }
}
</script>
<style>
.submit-btn{
  font-size:20px;
  font-weight: bold;
  height:80px;
  width:275px;
  font-size: 35px;
}
.inputs-wrapper{
    padding:50px;
    height: 60px;
}
input::placeholder{
   text-align: center;
}

#input-form{
  text-align: center;
  width: 100%;
  height: 80px;
  margin: 8px 0;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 15px;
  box-sizing: border-box;
  font-weight: bold;
  font-size: 45px;
}
#label-form{
  margin-left: 0px;
}
</style>
