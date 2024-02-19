<template>
  <StageStatisticsTable
    :user-id="userId"
    :rule="rule"
    :buki="buki"
    :linkEnabled="linkEnabled"
    :breakdown-rule-enabled="breakdownRuleEnabled"
    :breakdown-buki-enabled="breakdownBukiEnabled"
  >
    <template v-slot:ruleTable="slotProps">
      <RuleStatisticsTable
        :user-id="userId"
        :stage="slotProps.data.row.stageName"
        :buki="buki"
        :dense="true"
        :inner-mode="true"
        :columns-width="getColumnsWidth(slotProps.data)"
      />
    </template>
    <template v-slot:bukiTable="slotProps">
      <BukiStatisticsTable
        class="noPaddingX"
        :user-id="userId"
        :stage="slotProps.data.row.stageName"
        :rule="rule"
        :dense="true"
        :inner-mode="true"
        :columns-width="getColumnsWidth(slotProps.data)"
      />
    </template>
  </StageStatisticsTable>

</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import { useStore } from 'vuex'
import BukiStatisticsTable from '@/components/BukiStatisticsTable.vue'
import RuleStatisticsTable from '@/components/RuleStatisticsTable.vue'
import StageStatisticsTable from '@/components/StageStatisticsTable.vue'

export default defineComponent({
  name: 'StageStatisticsTableBreakdown',
  components: { BukiStatisticsTable, RuleStatisticsTable, StageStatisticsTable },
  props: {
    userId: {
      type: String,
      required: true
    },
    rule: {
      type: String
    },
    buki: {
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
    breakdownBukiEnabled: {
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
        slotData.stageNameElem.offsetWidth,
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
.link {
  border-bottom: 1px solid #1d1d1d;
  cursor: pointer;
}
.noPaddingX {
  padding-left: 0 !important;
  padding-right: 0 !important;
}
</style>