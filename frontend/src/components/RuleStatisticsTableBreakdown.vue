<template>
  <RuleStatisticsTable
    :user-id="userId"
    :stage="stage"
    :buki="buki"
    :linkEnabled="linkEnabled"
    :breakdown-buki-enabled="breakdownBukiEnabled"
    :breakdown-stage-enabled="breakdownStageEnabled"
  >
    <template v-slot:bukiTable="slotProps">
      <BukiStatisticsTable
        class="noPaddingX"
        :user-id="userId"
        :rule="slotProps.data.row.ruleName"
        :stage="stage"
        :dense="true"
        :inner-mode="true"
        :columns-width="getColumnsWidth(slotProps.data)"
      />
    </template>
    <template v-slot:stageTable="slotProps">
      <StageStatisticsTable
        :user-id="userId"
        :rule="slotProps.data.row.ruleName"
        :buki="buki"
        :dense="true"
        :inner-mode="true"
        :columns-width="getColumnsWidth(slotProps.data)"
      />
    </template>
  </RuleStatisticsTable>

</template>
  
<script lang="ts">
import { defineComponent } from 'vue'
import { useStore } from 'vuex'
import BukiStatisticsTable from '@/components/BukiStatisticsTable.vue'
import RuleStatisticsTable from '@/components/RuleStatisticsTable.vue'
import StageStatisticsTable from '@/components/StageStatisticsTable.vue'

export default defineComponent({
  name: 'RuleStatisticsTableBreakdown',
  components: { BukiStatisticsTable, RuleStatisticsTable, StageStatisticsTable },
  props: {
    userId: {
      type: String,
      required: true
    },
    stage: {
      type: String
    },
    buki: {
      type: String
    },
    linkEnabled: {
      type: Boolean,
      default: false
    },
    breakdownBukiEnabled: {
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
        slotData.ruleNameElem.offsetWidth,
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