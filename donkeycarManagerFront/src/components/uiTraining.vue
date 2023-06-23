<template>
  <div ref="uiSvg" id="svg-ui"></div>
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
      this.$refs.uiSvg.style.backgroundImage = `url( ${require(`../assets/svg/${n + 1}.svg`)} )`
    }
  }
}
</script>
<style scoped>
#svg-ui {
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}
</style>
