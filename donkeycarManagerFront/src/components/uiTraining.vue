<template>
  <img classs="svgUI" id="svg-ui">
</template>
<script>
export default {
  data () {
    return {
      boucle: null
    }
  },
  mounted () {
    document.getElementById('svg-ui').src = require('../assets/svg/1.svg')
    let x = 2
    this.boucle = setInterval(function () {
      if (x < 5) {
        document.getElementById('svg-ui').src = require('../assets/svg/' + x + '.svg')
        x += 1
      } else {
        x = 1
        document.getElementById('svg-ui').src = require('../assets/svg/' + x + '.svg')
      }
    }, 1500)
  },
  unmounted () {
    clearInterval(this.boucle)
  }
}
</script>
