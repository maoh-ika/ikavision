<template>
  <div class="row justify-center tableContainer">
    <div :style="{ display: 'flex', overflow: 'scroll',  width: '90%', height: '100%', }">
      <BattleCard
        v-for="sammary in newArrivals"
        class="q-mx-xs"
        :user-id="userId"
        :job-id="sammary.jobId"
        :result-id="sammary.resultId"
        :key="sammary.resultId"
      />
    </div>
  </div>
</template>
  
<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { round } from '@/modules/Utils'
import type { AnalysisResultSammary } from '@/modules/AnalysisResultApi'
import BattleCard from '@/components/BattleCard.vue'

export default defineComponent({
  name: 'NewArrivalBattles',
  components: { BattleCard },
  props: {
    userId: {
      type: String,
      default: 'splatoon3_environment'
    },
    pageSize: {
      type: Number,
      default: 20
    }
  },
  setup(props) {
    const t = useI18n()
    const $q = useQuasar()
    const store = useStore()

    onMounted(async () => {
      if (
        !store.getters['analysisResult/isSammaryPaginationLoaded'] &&
        anslysisSammaries.value.length < props.pageSize
      ) {
        try {
          $q.loading.show()
          await store.dispatch('analysisResult/fetchSammariesPagination', {userId: props.userId, pageSize: props.pageSize})
        } finally {
          $q.loading.hide()
        }
      }
    })
    
    const anslysisSammaries = computed(() => {
      const sammaries = store.getters['analysisResult/getSammariesPagination'](props.userId) as AnalysisResultSammary[]
      if (sammaries === undefined) {
        return []
      }
      return sammaries
    })

    const newArrivals = computed(() => {
      const results = anslysisSammaries.value.slice(0, props.pageSize)
      results.sort((a, b) => b.battleDate - a.battleDate)
      return results
    })

    return {
      newArrivals,
      round,
    }
  }
})
</script>

<style scoped>
.rowItem {
  font-size: 1rem;
}
.increase {
  color: red;
}
.decrease {
  color: blue;
}
.tableContainer {
  width: 100%;
  height: 300px;
}
</style>