<template>
<div>
<h1> Donkeycar Dashboard </h1>
    <div class="hidden">
      <vs-sidebar absolute v-model="active" open>
        <template #logo>
          <img class="logo" src="../assets/donkeycar.png">
        </template>
        <vs-sidebar-item id="home">
          <template #icon>
            <i class='bx bx-home'></i>
          </template>
          Home
        </vs-sidebar-item>
        <vs-sidebar-item id="cars">
          <template #icon>
            <i class='bx bx-grid-alt'></i>
          </template>
          voitures
        </vs-sidebar-item>
        <vs-sidebar-item id="waitingList">
          <template #icon>
            <i class='bx bxs-music'></i>
          </template>
          liste d'attente
        </vs-sidebar-item>
      </vs-sidebar>
    </div>
    <div class="table-wrapper" v-if="active === 'waitingList'">
      <vs-table >
        <template #thead>
          <vs-tr>
            <vs-th>
              Pseudo
            </vs-th>
            <vs-th>
              Status
            </vs-th>
            <vs-th>
              Ordre de passage
            </vs-th>
            <vs-th>
              Attente estimée
            </vs-th>
          </vs-tr>
        </template>
        <template #tbody>
          <vs-tr :key="i" v-for="(tr, i) in clients" :data="tr" >
            <vs-td>
              {{ tr.pseudo }}
            </vs-td>
            <vs-td>
            <vs-button class="edit-btn" color="#00b4d8" v-if="tr.status === 'drive'" > Drive a car </vs-button>
            <vs-button class="edit-btn" color="#faa307" v-if="tr.status === 'waiting'" > Waiting a car </vs-button>
            <vs-button class="edit-btn" color="#8338ec" v-if="tr.status === 'train'" >  recording data </vs-button>
            </vs-td>
            <vs-td>
            {{ tr.ordre }}
            </vs-td>
            <vs-td>
             <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg> {{tr.ordre*15}} Minutes
            </vs-td>
            <template #expand>
              <div class="expand-content">
                <div class="button-wrapper" >
                  <vs-row>
                    <vs-col vs-justify="center" vs-align="center" w="2">
                      <vs-button color="#7d33ff" relief @click="edit = tr, editProp = 'pseudo', editActive = true">
                        Change username
                      </vs-button>
                    </vs-col>
                    <vs-col vs-justify="center" vs-align="center" w="2">
                      <vs-button color="#7d33ff" relief @click="edit = tr, editProp = 'status', editActive = true">
                        Change status
                      </vs-button>
                    </vs-col>
                    <vs-col vs-justify="center" vs-align="center" w="2">
                      <vs-button color="#7d33ff" relief @click="edit = tr, editProp = 'rank', editActive = true">
                        Change rank in waiting board
                      </vs-button>
                    </vs-col>
                    <vs-col vs-justify="center" vs-align="center" w="2">
                      <vs-button border danger>
                        Remove User
                      </vs-button>
                    </vs-col>
                  </vs-row>
                </div>
              </div>
            </template>
          </vs-tr>
        </template>
      </vs-table>
    </div>
    <div class="cards-wrapper" v-if="active === 'cars'">
      <vs-card-group>
        <vs-card :key="i" v-for="(car, i) in cars" :data="car" >
          <template #title>
            <h3>{{car.name}}</h3>
          </template>
          <template #text>
            <p> IP : {{car.ip}} </p>
            <div class="center grid">
              <vs-row>
                <vs-col class="text-status" vs-type="flex" vs-justify="right" vs-align="right" w="6">
                  <p>Status : </p>
                </vs-col>
                <vs-col vs-type="flex" vs-justify="right" vs-align="right" w="6">
                  <vs-button color="#00b4d8" v-if="car.status === 'DRIVE'" > 🎮 Drive </vs-button>
                  <vs-button color="#8338ec" v-if="car.status === 'RECORING'" > 🎥 recording data </vs-button>
                  <vs-button color="#06d6a0" v-if="car.status === 'AI_ASSISTED'" > 🧪 AI assisted </vs-button>
                  <vs-button color="#fe5f55" v-if="car.status === 'MAINTAINANCE'" > 🧰 In maintainance </vs-button>
                </vs-col>
              </vs-row>
              <p v-if="car.user!=''"> Used by : <b>{{car.user}}</b> </p>
            </div>
          </template>
          <template #interactions>
            <vs-button danger icon>
              <i class='bx bx-heart'></i>
            </vs-button>
            <vs-button class="btn-chat" shadow primary>
              <i class='bx bx-chat' ></i>
              <span class="span">
                54
              </span>
            </vs-button>
          </template>
        </vs-card>
      </vs-card-group>
     </div>
      <vs-dialog v-model="editActive">
        <template #header>
            Changer le {{ editProp }}
        </template>
        <vs-input @keypress.enter="editActive = false" v-if="editProp == 'pseudo'" v-model="edit[editProp]"/>
        <vs-input type="number" @keypress.enter="editActive = false" v-if="editProp == 'rank'" v-model="edit[editProp]"/>
        <vs-select @change="editActive = false" block v-if="editProp == 'status'" placeholder="Select" v-model="edit[editProp]">
          <vs-option label="train" value="train">
            Train
          </vs-option>
          <vs-option label="drive" value="drive">
            Drive
          </vs-option>
          <vs-option label="wait" value="waiting">
            Wait
          </vs-option>
        </vs-select>
        <template #footer>
            <div class="con-footer">
              <vs-button success @click="editActive=false" >save</vs-button>
            </div>
         </template>
      </vs-dialog>
</div>
</template>
<script>

import clients from '../data/clients.js'
import cars from '../data/cars.js'

export default {
  data: () => ({
    edit: null,
    editProp: {},
    editActive: false,
    active: 'home',
    clients: clients,
    cars: cars
  })
}
</script>

<style>
.vs-card-content{
  width:300px !important ;
}
.text-status{
  padding-top:10px;
  text-align: right;
  font-size: 15px;
}
.cards-wrapper{
  padding-left: 260px;
}
.table-wrapper{
    padding-left: 260px;
}
.logo{
    width: 175px;
}
</style>
