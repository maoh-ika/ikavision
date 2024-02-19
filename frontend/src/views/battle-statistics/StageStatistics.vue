<template>
  <div class="full-width column items-center">
    <div>{{ $t('statistics.stageStatistics.desc') }}</div>
    <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
    <StageStatisticsTable :user-id="userId" :link-enabled="true"/>
  </div>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import StageStatisticsTable from '@/components/StageStatisticsTable.vue'

export default defineComponent({
  name: 'StageStatistics',
  components: { StageStatisticsTable },
  props: {
    userId: {
      type: String,
      required: true
    }
  }
})
</script>

<style scoped>
</style>