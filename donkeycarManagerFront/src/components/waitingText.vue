<template>
  <div>
    <span style="--i:1">E</span>
    <span style="--i:2">N</span>
    <span style="--i:2"> </span>
    <span style="--i:2"> </span>
    <span style="--i:3">A</span>
    <span style="--i:4">T</span>
    <span style="--i:5">T</span>
    <span style="--i:6">E</span>
    <span style="--i:7">N</span>
    <span style="--i:8">T</span>
    <span style="--i:9">E</span>
  </div>
</template>

<style scoped>
span {
  display: inline-block;
  font-weight: bold;
  font-size: 50px;
  animation: flip 5s infinite;
  animation-delay: calc(.2s * var(--i))
}
@keyframes flip {
  0%,80% {
    transform: rotateY(360deg)
  }
}
</style>
