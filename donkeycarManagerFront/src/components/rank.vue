<template>
<h1> Classement des meilleurs pilotes</h1>
</template>
<script>

import DonkeycarManagerService from '@/js/service.js'

const ip = DonkeycarManagerService.ip
const srv = new DonkeycarManagerService('http://' + ip + ':8000')

export default {
  data: () => ({
  }),
  created () {
    const that = this
  },
  methods: {
  }
}
</script>