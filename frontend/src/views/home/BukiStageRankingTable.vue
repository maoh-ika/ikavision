<template>
  <BukiRankingTable
    :make-ranking="makeRanking"
    :make-item-label="makeStageLabel"
    :rank-items="stages"
    :value-column-name="valueColumnName"
    :value-unit="valueUnit"
  />
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import type { BattleStage } from '@/models/Battle'
import BukiRankingTable from './BukiRankingTable.vue'

export interface BukiItem {
  bukiId: string
  value: string
  rocIn24h: number
}

export default defineComponent({
  name: 'BukiStageRankingTable',
  components: { BukiRankingTable },
  props: {
    makeRanking: {
      type: Function,
      default: () => {}
    },
    valueColumnName: {
      type: String,
      required: true
    },
    valueUnit: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const t = useI18n()
    const store = useStore()

    const stages = computed((): BattleStage[] => {
      const stages = store.getters['battleEnvironment/getAllStages']() as BattleStage[]
      stages.sort((a, b) => makeStageLabel(a) < makeStageLabel(b) ? -1 : 1)
      return stages
    })

    const makeStageLabel = (stage: BattleStage): string => {
      return t.t(`battleStage.${stage}`)
    }

    return {
      stages,
      makeStageLabel,
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
}
.carouselSlide {
  overflow-x: scroll;
  overflow-y: hidden;
}
</style>