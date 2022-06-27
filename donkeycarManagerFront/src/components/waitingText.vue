<template>
  <div>
    <span style="--i:1">E</span>
    <span style="--i:2">N</span>
    <span style="--i:3"> </span>
    <span style="--i:4"> </span>
    <span style="--i:5">A</span>
    <span style="--i:6">T</span>
    <span style="--i:7">T</span>
    <span style="--i:8">E</span>
    <span style="--i:9">N</span>
    <span style="--i:10">T</span>
    <span style="--i:11">E</span>
    <span style="--i:12">.</span>
    <span style="--i:13">.</span>
    <span style="--i:14">.</span>
  </div>
</template>

<style scoped>
div {
  margin-top: 40%;
  position: relative;
}
span {
  position: relative;
  display: inline-block;
  font-weight: bold;
  font-size: 50px;
  text-transform: uppercase;
  animation: flip 5s infinite;
  animation-delay: calc(.2s * var(--i))
}
@keyframes flip {
  0%,80% {
    transform: rotateY(360deg)
  }
}
</style>
