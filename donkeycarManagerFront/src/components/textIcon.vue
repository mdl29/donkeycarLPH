<template>
  <img :src="getImg(src)" />
</template>

<script>
export default {
  props: ["src"],
  methods: {
    getImg(src) {
      return require("../assets/controller/" + src)
    }
  }
}
</script>

<style scoped>
img {
  display: inline-block;
  width: 1.1em;
  height: 1.1em;
  background-image: var(--url);
  background-position: center center;
  background-size: cover;
  margin-bottom: -0.2em;
}
</style>
