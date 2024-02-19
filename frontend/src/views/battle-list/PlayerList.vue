<template>
    <div class="q-pa-md items-start">
      <q-list bordered separator class="">
        <q-item
          v-for="player in players"
        >
          <q-item-section class="row">
            <q-item-label>{{ player.name }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent, type PropType } from 'vue'
  import type { IkaPlayer } from '@/models/Player'
  
  export default defineComponent({
    name: 'PlayerList',
    props: {
      players: {
        type: Array as PropType<Array<IkaPlayer>>,
        required: true
      },
    },
    setup(props) {
    }
  })
  </script>
  
  <style scoped>
  </style>