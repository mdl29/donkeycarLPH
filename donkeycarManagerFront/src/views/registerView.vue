<template>
  <div class="main">
    <va-alert v-if="success === true" color="success" class="mb-4 alert" :title="'Enregistrement réussis'"> Vous pouvez vous diriger vers l'écran pour piloter une voiture !</va-alert>
    <va-alert v-if="success === false" color="danger" class="mb-4 alert" :title="'Impossible de vous enregistrer !'"> Veuillez réessayer ou bien demander de l'aide à un responsable du stand</va-alert>
    <h1 class="mainTitle">Inscris-toi pour piloter 🏎️ </h1>
    <RegisterForm :runTime="listOption" @success="success=$event" class="form"></RegisterForm>
  </div>
  <div class="option-container">
      <runOption :listOptions="listOption" @newParam="pushParam($event)"></runOption>
    </div>
</template>

<script>

import RegisterForm from '@/components/form.vue'
import runOption from '@/components/runOption.vue'

export default {
  components: {
    RegisterForm,
    runOption
  },
  data () {
    return {
      success: null,
      listOption: {}
    }
  },
  watch: {
    success: function () {
      setTimeout(() => { this.success = null }, 4000)
    }
  },
  created () {
    if (localStorage.getItem('registerOptions')) {
      try {
        this.listOption = JSON.parse(localStorage.getItem('registerOptions'))
      } catch (e) {
        console.log(e)
      }
    } else {
      this.listOption = { driveTime: '180', recordTime: '180' }
    }
  },
  methods: {
    pushParam (options) {
      this.listOption = options
      const parsed = JSON.stringify(options)
      localStorage.setItem('registerOptions', parsed)
    }
  }
}
</script>
<style scoped>
.alert{
  margin-top: 1%;
  text-align: left;
  font-size: 25px;
  width: 98%;
}
.form{
  padding-top: 5%;
}
.mainTitle{
  font-size: 50px;
}
.option-container{
  position: relative;
}

</style>
