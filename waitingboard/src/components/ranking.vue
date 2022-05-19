<template>
    <div id="ranking">
        <h1> Classement des meilleurs pilotes </h1>
        <ul> 
            <li class="podium-line" v-for="pilot in classement" v-if="pilot.rank===1">
                <vs-row>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="1">
                   🏆 
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="1">
                   <b>{{pilot.pseudo}}</b>
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="3">
                    <p>  Meilleur temps : {{pilot.bestTime}} </p>
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="3">
                    <p>  Voiture : {{pilot.car}} </p>
                </vs-col>
                </vs-row> 
            </li>
            <li class="podium-line" v-for="pilot in classement" v-if="pilot.rank===2">
                <vs-row>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="1">
                   🥈
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="1">
                   <b>{{pilot.pseudo}}</b>
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="3">
                    <p>  Meilleur temps : {{pilot.bestTime}} </p>
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="3">
                    <p>  Voiture : {{pilot.car}} </p>
                </vs-col>
                </vs-row> 
            </li>
            <li class="podium-line" v-for="pilot in classement" v-if="pilot.rank===3">
                <vs-row>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="1">
                   🥉 
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="1">
                   <b>{{pilot.pseudo}}</b>
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="3">
                    <p>  Meilleur temps : {{pilot.bestTime}} </p>
                </vs-col>
                <vs-col  vs-type="flex" vs-justify="center" vs-align="center" w="3">
                    <p>  Voiture : {{pilot.car}} </p>
                </vs-col>
                </vs-row> 
            </li>
        </ul>
    </div>
</template>
<script>

import rank from '../data/classement.js'

export default {
  data: () => ({
      classement: rank
  })
}
</script>
<style>
.podium-line{
    padding:30px;
}
</style>