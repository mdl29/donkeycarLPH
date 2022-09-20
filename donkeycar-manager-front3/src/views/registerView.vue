<template>
  <div class="main">
    <va-alert v-if="success === true" color="success" class="mb-4 alert" :title="'Enregistrement réussis'"> Vous pouvez vous diriger vers l'ecran pour piloter une voiture !</va-alert>
    <va-alert v-if="success === false" color="danger" class="mb-4 alert" :title="'Impossible de vous enregistrer !'"> Veuillez réessayer ou bien demander de l'aide à un responsable du stand</va-alert>
    <h1 class="mainTitle">Inscris toi pour piloter 🏎️ </h1>
    <RegisterForm @success="success=$event" class="form"></RegisterForm>
  </div>
</template>

<script>

import RegisterForm from '@/components/form.vue'

export default {
  components: {
    RegisterForm
  },
  data () {
    return {
      success: 'none'
    }
  }
}
</script>
<style>
.alert{
  text-align: left !important;
  font-size: 25px;
  width: 98%;
}
.form{
  padding-top: 5%;
}
.mainTitle{
  margin-top: 45px;
  font-size: 50px;
}

</style>
