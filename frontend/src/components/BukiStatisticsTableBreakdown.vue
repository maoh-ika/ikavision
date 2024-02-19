<template>
  <BukiStatisticsTable
    :user-id="userId"
    :rule="rule"
    :stage="stage"
    :linkEnabled="linkEnabled"
    :breakdown-rule-enabled="breakdownRuleEnabled"
    :breakdown-stage-enabled="breakdownStageEnabled"
  >
    <template v-slot:ruleTable="slotProps">
      <RuleStatisticsTable
        :user-id="userId"
        :buki="slotProps.data.row.bukiId"
        :stage="stage"
        :dense="true"
        :inner-mode="true"
        :columns-width="getColumnsWidth(slotProps.data)
      "/>
    </template>
    <template v-slot:stageTable="slotProps">
      <StageStatisticsTable
        :user-id="userId"
        :buki="slotProps.data.row.bukiId"
        :rule="rule"
        :dense="true"
        :inner-mode="true"
        :columns-width="getColumnsWidth(slotProps.data)"
      />
    </template>
  </BukiStatisticsTable>

</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import { useStore } from 'vuex'
import BukiStatisticsTable from '@/components/BukiStatisticsTable.vue'
import RuleStatisticsTable from '@/components/RuleStatisticsTable.vue'
import StageStatisticsTable from '@/components/StageStatisticsTable.vue'

export default defineComponent({
  name: 'BukiStatisticsTableBreakdown',
  components: { BukiStatisticsTable, RuleStatisticsTable, StageStatisticsTable },
  props: {
    userId: {
      type: String,
      required: true
    },
    rule: {
      type: String
    },
    stage: {
      type: String
    },
    linkEnabled: {
      type: Boolean,
      default: false
    },
    breakdownRuleEnabled: {
      type: Boolean,
      default: false
    },
    breakdownStageEnabled: {
      type: Boolean,
      default: false
    },
    dense: {
      type: Boolean,
      default: false
    },
    hideHeader: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const store = useStore()

    const getColumnsWidth = (slotData: any) => {
      return [
        slotData.bukiIdElem.offsetWidth,
        slotData.battleCountElem.offsetWidth,
        slotData.winRateElem.offsetWidth,
        slotData.winCountElem.offsetWidth,
        slotData.loseCountElem.offsetWidth,
        slotData.killAveElem.offsetWidth,
        slotData.deathAveElem.offsetWidth,
        slotData.spAveElem.offsetWidth
      ]
    }

    return {
      getColumnsWidth
    }
  }
})
</script>

<style scoped>
</style>