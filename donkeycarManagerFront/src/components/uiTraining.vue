<template>
  <img id="svg-ui">
</template>
<script>
export default {
  data () {
    return {
    }
  },
  created () {
    let x = 1
    setInterval(function () {
      if (x <= 4) {
        console.log('hello')
        document.getElementById('svg-ui').src = require('../assets/svg/' + x + '.svg')
        x += 1
      } else {
        x = 1
      }
    }, 30000)
  }
}
</script>
<style>

</style>
