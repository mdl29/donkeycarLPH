<template>
  <div>
    <h1 class="title-header"> Devenir pilote en accédant à la liste d'attente </h1>
    <div class="inputs-wrapper">
      <vs-row align="center" justify="center">
        <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="6">
          <vs-input class="input" color="#7d33ff" shadow border type="text"  v-model="pseudo" label-placeholder="Pseudo" style="padding:20px" required="required">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" style="fill: rgba(84, 83, 83, 1);transform: ;msFilter:;"><path d="M12 2a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm0 8a3 3 0 1 1 3-3 3 3 0 0 1-3 3zm9 11v-1a7 7 0 0 0-7-7h-4a7 7 0 0 0-7 7v1h2v-1a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v1z"></path></svg>
            </template>
            <template v-if="pseudoBlank == true " #message-danger>
              veuillez choisir un pseudo
            </template>
          </vs-input>
        </vs-col>
        <vs-col vs-type="flex" vs-justify="center" vs-align="center" w="6">
          <vs-input color="#7d33ff" class="input" shadow border type="tel" v-model="tel" label-placeholder="Numéro de téléphone" style="padding:20px" required="required">
            <template #icon>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" style="fill: rgba(84, 83, 83, 1);transform: ;msFilter:;"><path d="M17.707 12.293a.999.999 0 0 0-1.414 0l-1.594 1.594c-.739-.22-2.118-.72-2.992-1.594s-1.374-2.253-1.594-2.992l1.594-1.594a.999.999 0 0 0 0-1.414l-4-4a.999.999 0 0 0-1.414 0L3.581 5.005c-.38.38-.594.902-.586 1.435.023 1.424.4 6.37 4.298 10.268s8.844 4.274 10.269 4.298h.028c.528 0 1.027-.208 1.405-.586l2.712-2.712a.999.999 0 0 0 0-1.414l-4-4.001zm-.127 6.712c-1.248-.021-5.518-.356-8.873-3.712-3.366-3.366-3.692-7.651-3.712-8.874L7 4.414 9.586 7 8.293 8.293a1 1 0 0 0-.272.912c.024.115.611 2.842 2.271 4.502s4.387 2.247 4.502 2.271a.991.991 0 0 0 .912-.271L17 14.414 19.586 17l-2.006 2.005z"></path></svg>
            </template>
            <template v-if="telBlank == true " #message-danger>
              veuillez renseigner votre numéro de téléphone
            </template>
          </vs-input>
        </vs-col>
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

export default {
  data: () => ({
    pseudo: '',
    tel: '',
    popup: false,
    pseudoBlank: false,
    telBlank: false,
    numero: 0,
    attente: 15
  }),
  methods: {
    check () {
      if (this.pseudo === '') {
        this.pseudoBlank = true
      }
      if (this.tel === '') {
        this.telBlank = true
      } else {
        this.numero = Math.floor(Math.random() * 150)
        this.popup = true
      }
    },
    redirect () {
      this.$router.push('/')
    },
    addUser () {
      // const numero = clients.length + 1
      // clients.push(
      //   {
      //     ordre: numero,
      //     timestamp: '',
      //     pseudo: this.pseudo,
      //     tel: this.tel,
      //     status: 'waiting'
      //   }
      // )
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
    padding:150px;
}
</style>
