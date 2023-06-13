<template>
  <img classs="svgUI" ref="uiSvg" id="svg-ui">
</template>
<script>
const imageCount = 4
export default {
  data () {
    return {
      loop: null
    }
  },
  mounted () {
    let image = 0
    this.setImage(image)
    const that = this
    this.loop = setInterval(function () {
      image = (image + 1) % imageCount
      that.setImage(image)
    }, 17000)
  },
  unmounted () {
    clearInterval(this.loop)
  },
  methods: {
    setImage (n) {
      this.$refs.uiSvg.src = require(`../assets/svg/${n + 1}.svg`)
    }
  }
}
</script>
