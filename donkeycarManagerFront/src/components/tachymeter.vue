<template>
  <div class="tachymeter">
    <svg
      style="overflow: visible"
      :class="{ popup: popup }"
      xmlns="http://www.w3.org/2000/svg"
      xmlns:xlink="http://www.w3.org/1999/xlink"
      viewBox="0 0 162.43 88.26"
    >
      <defs>
        <linearGradient
          id="gradient"
          data-name="gradient"
          x1="0"
          y1="42.69"
          x2="162.43"
          y2="42.69"
          gradientUnits="userSpaceOnUse"
        >
          <stop offset="0" stop-color="#7ff47f" />
          <stop offset="1" stop-color="#f15a24" />
        </linearGradient>
      </defs>
      <path
        class="cls-1"
        d="m62.39,85.17c3.71-6.53,10.71-10.94,18.76-10.94s15.21,4.5,18.88,11.15l59.67-34.01c2.71-1.55,3.55-5.05,1.85-7.67C144.47,17.4,114.84,0,81.15,0S17.99,17.3.89,43.48c-1.71,2.62-.87,6.13,1.84,7.68l59.66,34Z"
      />
      <path
        class="cls-2"
        :style="{ transform: `rotate(${angle}deg)` }"
        d="m70.65,78.19L81.15,7.23l10.5,70.96c.86,5.8-3.15,11.2-8.95,12.05-6.91,1.14-13.17-5.17-12.05-12.05h0Z"
      />
    </svg>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const popup = ref(false)

const props = defineProps({
  coefficient: Number //0 min, 1 max
})

const angle = computed(() => {
  return props.coefficient * 120 - 60 //[-60°; +60°]
})

function startAnimPopup() {
  if (popup.value) return
  popup.value = true
  setTimeout(() => {
    popup.value = false
  }, 160)
}

watch(angle, () => {
  startAnimPopup()
})
</script>

<style scoped>
.tachymeter {
  display: flex;
  padding: 20%;
}
.cls-1 {
  fill: url(#gradient);
}

.cls-2 {
  fill: #4f4f4f;
  transform-origin: bottom;
  transition-duration: 0.5s;
  transition-timing-function: cubic-bezier();
}

.popup {
  transition-duration: 0.08s;
  transform: scale(1.2);
}
</style>
