<template>
  <div class="row items-center" :aria-label="info">
    <div class="text-bold" style="font-size:1.6rem">{{ title }}</div>
    <q-icon v-if="info" class="q-ml-sm" name="info" size="2rem" color="positive" >
      <q-tooltip max-width="300px">
        <div>
          {{ info }}
        </div>
      </q-tooltip>
    </q-icon>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'SectionTitle',
  props: {
    title: {
      type: String,
      required: true
    },
    info: {
      type: String
    }
  },
  setup(props) {
    return {
    }
  }
})
</script>

<style scoped>
</style>