<template>
  <div class="full-width column items-center">
    <div>{{ $t('statistics.sammary.desc') }}</div>
    <q-separator class="q-mt-sm q-mb-md" style="width:60%"/>
    <StatisticsSammary :user-id="userId" />
  </div>
</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import StatisticsSammary from '@/components/StatisticsSammary.vue'

export default defineComponent({
  name: 'TotalStatistics',
  components: {
    StatisticsSammary
  },
  props: {
    userId: {
      type: String,
      required: true
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