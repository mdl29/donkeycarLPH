<template>
<div>
    <h1> Waiting Board </h1>
    <div class="table-wrapper">
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
          <vs-tr
            :key="i"
            v-for="(tr, i) in clients"
            :data="tr"
          >
            <vs-td>
              {{ tr.pseudo }}
            </vs-td>
            <vs-td>
            <vs-button color="#00b4d8" v-if="tr.status === 'drive'" > Drive a car </vs-button>

            <vs-button color="#faa307" v-if="tr.status === 'waiting'" > Waiting a car </vs-button>

            <vs-button color="#8338ec" v-if="tr.status === 'train'" >  recording data </vs-button>
            </vs-td>
            <vs-td>
            {{ tr.ordre }}
            </vs-td>
            <vs-td>
             <svg xmlns="http://www.w3.org/2000/svg" width="35" height="24" style="fill: rgba(255, 183, 3, 1);transform: ;msFilter:;"><path d="m20.145 8.27 1.563-1.563-1.414-1.414L18.586 7c-1.05-.63-2.274-1-3.586-1-3.859 0-7 3.14-7 7s3.141 7 7 7 7-3.14 7-7a6.966 6.966 0 0 0-1.855-4.73zM15 18c-2.757 0-5-2.243-5-5s2.243-5 5-5 5 2.243 5 5-2.243 5-5 5z"></path><path d="M14 10h2v4h-2zm-1-7h4v2h-4zM3 8h4v2H3zm0 8h4v2H3zm-1-4h3.99v2H2z"></path></svg> {{tr.ordre*15}} Minutes
            </vs-td>
          </vs-tr>
        </template>
      </vs-table>
    </div>
</div>
</template>
<script>
import clients from '../data/clients.js'

export default {
  data () {
    return {
      time: 0,
      clients: clients
    }
  }
}
</script>

<style>
.table-wrapper{
  text-align: left !important;
  padding: 20px;
}
</style>
