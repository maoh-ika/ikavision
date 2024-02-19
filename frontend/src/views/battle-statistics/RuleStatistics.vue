<template>
  <div class="full-width column items-center">
    <div>{{ $t('statistics.ruleStatistics.desc') }}</div>
    <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
    <RuleStatisticsTable :user-id="userId" :link-enabled="true" />
  </div>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import RuleStatisticsTable from '@/components/RuleStatisticsTable.vue'

export default defineComponent({
  name: 'RuleStatistics',
  components: { RuleStatisticsTable },
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