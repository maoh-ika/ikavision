<template>
  <BukiRankingTable
    :make-ranking="makeRanking"
    :make-item-label="makeRuleLabel"
    :rank-items="rules"
    :value-column-name="valueColumnName"
    :value-unit="valueUnit"
  />
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import type { BattleRule } from '@/models/Battle'
import BukiRankingTable from './BukiRankingTable.vue'

export interface BukiItem {
  bukiId: string
  value: string
  rocIn24h: number
}

export default defineComponent({
  name: 'BukiRuleRankingTable',
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
    
    const rules = computed((): BattleRule[] => {
      const rules = store.getters['battleEnvironment/getAllRules']() as BattleRule[]
      rules.sort((a, b) => makeRuleLabel(a) < makeRuleLabel(b) ? -1 : 1)
      return rules
    })
    
    const makeRuleLabel = (rule: BattleRule): string => {
      return t.t(`battleRule.${rule}`)
    }
    
    return {
      rules,
      makeRuleLabel
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
.carousel {
}
.carouselSlide {
  overflow-x: scroll;
  overflow-y: hidden;

}
</style>