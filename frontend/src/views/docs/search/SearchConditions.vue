<template>
<q-layout view="hhh lpr fff">
  <q-page class="q-pa-md column items-center root">
    <ConditionsMD :style="{width: '80%'}"/>
  </q-page>
</q-layout>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import ConditionsMD from '@/assets/docs/search/SearchConditions.md'

export default defineComponent({
  name: 'SearchConditions',
  components: {ConditionsMD}
})
</script>

<style scoped>
:deep(td) {
  border: 1px solid #ddd;
  padding: 8px;
}
:deep(table) {
  border-spacing: 0px;
}
</style>