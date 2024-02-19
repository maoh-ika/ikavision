<template>
  <q-table
    flat bordered
    :dense="dense"
    :hide-header="hideHeader"
    class="full-width q-my-md cst-sticky-header "
    align="left"
    :rows="items"
    :columns="columns"
    :hide-pagination="true"
    :pagination="{rowsPerPage: 1000}"
    :no-data-label="$t('statistics.ruleStatistics.noData')"
    row-key="ruleName"
  >
    <template v-slot:header="props">
      <q-tr :props="props">
        <q-th
          v-for="col, idx in props.cols"
          :ref="col.name"
          :key="col.name"
          :props="props"
          :style="getHeaderStyle(col, idx)"
        >
          {{ getHeaderLabel(col, idx) }}
        </q-th>
      </q-tr>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td v-if="breakdownBukiEnabled || breakdownStageEnabled" auto-width>
          <q-btn size="sm" flat round dense @click="props.expand = !props.expand" :icon="props.expand ? 'remove' : 'add'" />
        </q-td>
        <q-td key="ruleName" :props="props" @click="() => rowSelected(props.row)" :style="getColumnStyle(0, props)">
          <span :class="{ link: linkEnabled }">{{ $t(`battleRule.${props.row.ruleName}`) }}</span>
        </q-td>
        <q-td key="battleCount" :props="props" :style="getColumnStyle(1, props)">
          {{ props.row.battleCount }}
        </q-td>
        <q-td key="winRate" :props="props" :style="getColumnStyle(2, props)">
          {{ `${Math.round(props.row.winRate * 1000) / 10}%` }}
        </q-td>
        <q-td key="winCount" :props="props" :style="getColumnStyle(3, props)">
          {{ props.row.winCount }}
        </q-td>
        <q-td key="loseCount" :props="props" :style="getColumnStyle(4, props)">
          {{ props.row.loseCount }}
        </q-td>
        <q-td key="killAve" :props="props" :style="getColumnStyle(5, props)">
          {{ `${Math.round(props.row.killAve * 10) / 10}` }}
        </q-td>
        <q-td key="deathAve" :props="props" :style="getColumnStyle(6, props)">
          {{ `${Math.round(props.row.deathAve * 10) / 10}` }}
        </q-td>
        <q-td key="spAve" :props="props" :style="getColumnStyle(7, props)">
          {{ Math.round(props.row.spAve * 10) / 10 }}
        </q-td>
      </q-tr>
      <q-tr v-if="breakdownBukiEnabled && props.expand" :props="props">
        <q-td auto-width>{{ $t('general.breakdown') }}</q-td>
        <q-td class="noPaddingX" colspan="100%">
          <slot name="bukiTable" :data="getSlotData(props.row)" />
        </q-td>
      </q-tr>
      <q-tr v-else-if="breakdownStageEnabled && props.expand" :props="props">
        <q-td auto-width>{{ $t('general.breakdown') }}</q-td>
        <q-td class="noPaddingX" colspan="100%">
          <slot name="stageTable" :data="getSlotData(props.row)" />
        </q-td>
      </q-tr>
    </template>
  </q-table>
</template>
  
<script lang="ts">
import { defineComponent, type PropType, computed, ref } from 'vue'
import type { QTableColumn } from 'quasar'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import {
  calcWinRate,
  calcKillAve,
  calcDeathAve,
  calcSpAve,
  calcWinLoseCount,
  calcBattleCount
} from '@/modules/Statistics'
import type { AnalysisResultSammary } from '@/modules/AnalysisResultApi'
import type { BattleStatistics } from '@/modules/BattleStatisticsApi'
import type { BattleRule, BattleStage } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'

interface RuleItem {
  ruleName: string
  winRate: number
  winCount: number
  loseCount: number
  killAve: number
  deathAve: number
  spAve: number
  battleCount: number
}

export default defineComponent({
  name: 'RuleStatisticsTable',
  components: {},
  props: {
    userId: {
      type: String,
      required: true
    },
    resultIds: {
      type: Array as PropType<String[]>
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
    },
    columnsWidth: {
      type: Array as PropType<Number[]>
    },
    innerMode: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    const t = useI18n()
    const store = useStore()
    const router = useRouter()
    
    const ruleName = ref()
    const battleCount = ref()
    const winRate = ref()
    const winCount = ref()
    const loseCount = ref()
    const killAve = ref()
    const deathAve = ref()
    const spAve = ref()
    
    const stageFilter = props.stage as BattleStage
    const bukiFilter = props.buki as MainWeapon
    
    const statistics = computed(() => {
      return store.getters['battleStatistics/getMasterStatistics'](props.userId) as BattleStatistics
    })
    
    const items = computed((): RuleItem[] => {
      const statis = statistics.value
      if (statis === undefined) {
        return []
      }
      const rules = new Set<BattleRule>()
        statis.bukiPerformances.forEach(perf => {
        perf.results.forEach(res => rules.add(res.rule))
      })
      const _items: RuleItem[] = []
      rules.forEach(rule => {
        const winLose = calcWinLoseCount(statis.bukiPerformances, rule, stageFilter, bukiFilter)
        _items.push({
          ruleName: rule,
          winRate: calcWinRate(statis.bukiPerformances, rule, stageFilter, bukiFilter),
          winCount: winLose[0],
          loseCount: winLose[1],
          killAve: calcKillAve(statis.bukiPerformances, rule, stageFilter, bukiFilter),
          deathAve: calcDeathAve(statis.bukiPerformances, rule, stageFilter, bukiFilter),
          spAve: calcSpAve(statis.bukiPerformances, rule, stageFilter, bukiFilter),
          battleCount: winLose[0] + winLose[1]
        })
      })
      return _items
    })

    const columns: QTableColumn[] = [
      { name: 'ruleName', label: t.t('statistics.ruleStatistics.ruleName'), field: 'ruleName', align: 'left', sortable: true },
      { name: 'battleCount', label: t.t('statistics.sammary.allBattleCount'), field: 'battleCount', align: 'left', sortable: true },
      { name: 'winRate', label: t.t('statistics.winRate'), field: 'winRate', align: 'left', sortable: true },
      { name: 'winCount', label: t.t('statistics.sammary.winCount'), field: 'winCount', align: 'left', sortable: true },
      { name: 'loseCount', label: t.t('statistics.sammary.loseCount'), field: 'loseCount', align: 'left', sortable: true },
      { name: 'killAve', label: t.t('statistics.sammary.killAve'), field: 'killAve', align: 'left', sortable: true },
      { name: 'deathAve', label: t.t('statistics.sammary.deathAve'), field: 'deathAve', align: 'left', sortable: true },
      { name: 'spAve', label: t.t('statistics.sammary.spAve'), field: 'spAve', align: 'left', sortable: true },
    ]
    if (props.breakdownBukiEnabled) {
      columns.unshift({ name: 'breakdownBuki', label: t.t('statistics.ruleStatistics.breakdownBuki'), field: '', align: 'left'},)
    } else if (props.breakdownStageEnabled) {
      columns.unshift({ name: 'breakdownStage', label: t.t('statistics.ruleStatistics.breakdownStage'), field: '', align: 'left'},)
    }
    
    const rowSelected = (row: RuleItem) => {
      if (props.linkEnabled) {
        router.push({ name: 'ruleStatistics', params: {
          rule: row.ruleName
        }})
      }
    }
    
    const getSlotData = (row: any) => {
      return {
        row,
        ruleNameElem: ruleName.value[0].$el,
        battleCountElem: battleCount.value[0].$el,
        winRateElem: winRate.value[0].$el,
        winCountElem: winCount.value[0].$el,
        loseCountElem: loseCount.value[0].$el,
        killAveElem: killAve.value[0].$el,
        deathAveElem: deathAve.value[0].$el,
        spAveElem: spAve.value[0].$el
      }
    }

    const getHeaderLabel = (column: any, colIndex: number): any => {
      if (props.innerMode) {
        return colIndex === 0 ? column.label : ''
      } else {
        return column.label
      }
    }
    
    const getHeaderStyle = (colIndex: number, attrs: any): any => {
      const style: any = {}
      if (props.innerMode) {
        style.backgroundColor = '#fafafa'
      }
      return style
    }

    const getColumnStyle = (colIndex: number, attrs: any): any => {
      const style: any = {}
      if (props.columnsWidth !== undefined && colIndex < props.columnsWidth.length) {
        style.width = `${props.columnsWidth[colIndex]}px`
      }
      if (attrs.dense) {
        style.paddingLeft = '16px'
        style.paddingRight = '16px'
      }
      return style
    }

    return {
      ruleName,
      battleCount,
      winRate,
      winCount,
      loseCount,
      killAve,
      deathAve,
      spAve,
      columns,
      items,
      rowSelected,
      getSlotData,
      getHeaderLabel,
      getHeaderStyle,
      getColumnStyle 
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