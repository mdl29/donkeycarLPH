<template>
  <div class="button-container">
    <a @click="showModal = !showModal"> <img src="../assets/icons/settings.svg" ></a>
  </div>
    <va-modal  v-model="showModal" title="Register settings"  >
      <template #content="{ ok }">
        <va-card-title>
        Register settings
        </va-card-title>
        <va-card-content>
          <div class="param-wrapper">
              <va-checkbox class="mb-4" v-model="drive" label="Drive" />
              <div class="time-containeur">
                <label>time</label>
                <va-input style="width: 75px;" class="mb-4" v-model="options.driveTime" />
                <label>s</label>
              </div>
          </div>
          <div class="param-wrapper" >
              <va-checkbox class="mb-4" v-model="record" label="Record" />
              <div class="time-containeur">
                <label>time</label>
                <va-input style="width: 75px;" class="mb-4" v-model="options.recordTime" />
                <label>s</label>
              </div>
          </div>
        </va-card-content>
        <va-card-actions>
          <va-button @click="ok" v-on:click="pushParam()" color="success">Save settings</va-button>
        </va-card-actions>
    </template>
    </va-modal>
</template>
<script>
export default {
  props: {
    listOptions: Object
  },
  data () {
    return {
      showModal: false,
      options: this.listOptions,
      drive: true,
      record: true

    }
  },
  methods: {
    pushParam () {
      if (this.drive === false) {
        this.options.driveTime = '0'
      } else if (this.record === false) {
        this.options.recordTime = '0'
      }
      console.log(this.options)
      this.$emit('newParam', this.options)
    }
  }
}
</script>
<style>
.time-container {
  display: flex;
  align-items: center;
  justify-content: center;
}
.button-container{
  position: fixed;
  right: 0;
  bottom: 0;
}
label{
  padding: 10px;
}
</style>
