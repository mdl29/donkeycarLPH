<template>
  <div class="main">
    <va-alert v-if="success === true" color="success" class="mb-4 alert" :title="'Enregistrement réussis'"> Vous pouvez vous diriger vers l'ecran pour piloter une voiture !</va-alert>
    <va-alert v-if="success === false" color="danger" class="mb-4 alert" :title="'Impossible de vous enregistrer !'"> Veuillez réessayer ou bien demander de l'aide à un responsable du stand</va-alert>
    <h1 class="mainTitle">Inscris toi pour piloter 🏎️ </h1>
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
      listOption: { driveTime: '180', recordTime: '180' }
    }
  },
  watch: {
    success: function () {
      const that = this
      setTimeout(function () { that.success = null }, 4000)
    }
  },
  methods: {
    pushParam (options) {
      this.listOption = options
    }
  }
}
</script>
<style>
.alert{
  margin-top: 1% !important;
  text-align: left !important;
  font-size: 25px;
  width: 98%;
}
.form{
  padding-top: 5%;
}
.mainTitle{
  margin-top: 45px;
  font-size: 50px !important;
}
.option-container{
  position: relative;
}

</style>
