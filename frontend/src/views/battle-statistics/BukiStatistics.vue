<template>
  <div class="full-width column items-center">
    <div>{{ $t('statistics.bukiStatistics.desc') }}</div>
    <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
    <BukiStatisticsTable :user-id="userId" :link-enabled="true" />
  </div>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import BukiStatisticsTable from '@/components/BukiStatisticsTable.vue'

export default defineComponent({
  name: 'BukiStatistics',
  components: { BukiStatisticsTable },
  props: {
    userId: {
      type: String,
      required: true
    }
  },
  setup(props) {
  }
})
</script>

<style scoped>
</style>