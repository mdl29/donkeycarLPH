<template>
  <div class="form">
    <div class="row align--center">
      <div class="flex xs12">
        <input type="text" placeholder="Entrez votre pseudo" id="input-form" required="required" v-model="pseudo" v-on:keyup.enter="addUser()" maxlength="16">
      </div>
      <div class="flex xs12 button-wrapper" id="button-wrapper">
        <va-button id="submit-button" :loading="click"  size="large" color="info" gradient class="mr-4 mb-2" @click="addUser()">S'enregistrer</va-button>
      </div>
    </div>
  </div>
</template>

<script>
import DonkeycarManagerService from '@/js/service.js'

const ip = DonkeycarManagerService.ip
const srv = new DonkeycarManagerService('http://' + ip + ':8000')

export default {
  name: 'RegisterForm',
  props: {
    runTime: Object
  },
  data () {
    return {
      success: 'none',
      pseudo: '',
      click: false
    }
  },
  methods: {
    async addUser () {
      this.click = true
      const newPseudo = this.pseudo
      this.pseudo = ''
      if (newPseudo.length === 0) {
        this.click = false
        return
      }
      const players = await srv.getPlayerByPseudo(newPseudo)
      if (players.length === 0) {
        players[0] = await srv.createPlayer(newPseudo)
      }
      const response = await srv.addJobs(players[0].player_id, parseInt(this.runTime.driveTime), parseInt(this.runTime.recordTime))
      if (response === 404) {
        this.success = false
      } else {
        this.success = true
      }
      this.$emit('success', this.success)
      this.click = false
    }
  }
}

</script>
<style scoped>
form{
  text-align: center;
}
.button-wrapper{
  padding-top: 65px;
}
#input-form{
  text-align: center;
  width: 90%;
  height: 80px;
  display: inline-block;
  border: 1px solid #ccc;
  border-radius: 15px;
  box-sizing: border-box;
  font-weight: bold;
  font-size: 45px;
}
#submit-button{
  font-weight: bold;
  height:80px;
  width:300px;
  font-size: 35px;
}
</style>
