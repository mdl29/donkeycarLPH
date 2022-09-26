<template>
  <div>
    <template v-for="part in messageComponents" :key="part.index">
      <span v-if="part.text">
        {{ part.text }}
      </span>
      <textIcon :src="part.img" v-if="part.img" />
    </template>
  </div>
</template>

<script>
import textIcon from '@/components/textIcon.vue'
export default {
  components: {
    textIcon
  },
  props: ['message'],
  computed: {
    messageComponents () {
      const str = this.message
      const groups = str.split(/[\][]/g)
      const res = []
      let type = 'text'
      let index = 0
      for (const m of groups) {
        if (type === 'text') {
          res.push({ text: m, index })
          type = 'img'
        } else {
          res.push({ img: `PS4_${m}.png`, index })
          type = 'text'
        }
        index++
      }
      return res
    }
  }
}
</script>
