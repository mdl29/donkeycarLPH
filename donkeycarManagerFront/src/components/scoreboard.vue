<template>
  <div class="wrapper">
    <div class="item" v-for="item in list" :key="list.player">
      <div>{{ item.player }}</div>
      <div>{{ Math.floor(item.time / 10) / 100 }}s</div>
    </div>
  </div>
</template>

<script>
import DonkeycarManagerService from '@/js/service.js'
const ip = DonkeycarManagerService.ip
const srv = new DonkeycarManagerService('http://' + ip + ':8000')

export default {
  computed: {
    list() {
      const map = new Map();
      const races = srv.fetchRaces(0, 500)
        .forEach(race => {
          const player = race.player.player_pseudo;
          const time = race.laptimers.map(laptimer => laptimer.duration).reduce(Math.min);
          if (!map.has(player) || map.get(player) > time) {
            map.set(player, time);
          }
        });
      return Array.from(map).map(a => { player: a[0], time: a[1] });
    }
  }
}
</script>

<style scoped>
</style>
