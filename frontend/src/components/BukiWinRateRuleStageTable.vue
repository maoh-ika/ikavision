<template>
  <q-table
    flat bordered
    class="q-my-md cst-sticky-header "
    align="left"
    :rows="items"
    :columns="columns"
    :hide-pagination="true"
    :pagination="{rowsPerPage: 1000}"
    :no-data-label="$t('statistics.bukiStatistics.noData')"
    row-key="stage"
    column-sort-order="da"
    binary-state-sort
  >
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="number" :props="props">
          {{ props.rowIndex + 1 }}
        </q-td>
        <q-td key="stage" :props="props">
          <div class="row items-center q-pa-sm">
            <div>
              {{ $t(`battleStage.${props.row.stage}`) }}
            </div>
          </div>
        </q-td>
        <q-td key="usageArea" :props="props" >
          {{ rateView(props.row.usageArea) }}
        </q-td>
        <q-td key="usageHoko" :props="props" >
          {{ rateView(props.row.usageHoko) }}
        </q-td>
        <q-td key="usageYagura" :props="props" >
          {{ rateView(props.row.usageYagura) }}
        </q-td>
        <q-td key="usageAsari" :props="props" >
          {{ rateView(props.row.usageAsari) }}
        </q-td>
        <q-td key="usageNawabari" :props="props" >
          {{ rateView(props.row.usageNawabari) }}
        </q-td>
        <q-td>
          <q-btn size="sm" flat round dense @click="props.expand = !props.expand" :icon="props.expand ? 'remove' : 'add'" />
        </q-td>
      </q-tr>
      <q-tr v-if="props.expand" :props="props">
        <q-td colspan="100%">
          <BukiWinRateRuleHistoryChart class="column" :buki="buki" :stage="props.row.stage" :rules="rules" :height="320" />
        </q-td>
      </q-tr>
    </template>
  </q-table>
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import type { QTableColumn } from 'quasar'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { calcWinRate } from '@/modules/Statistics'
import type { BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { round } from '@/modules/Utils'
import type { BattleRule, BattleStage } from '@/models/Battle'
import BukiWinRateRuleHistoryChart from '@/components/BukiWinRateRuleHistoryChart.vue'
import type { MainWeapon } from '@/models/Buki'

interface BukiItem {
  stage: BattleStage
  usageNawabari: number
  usageArea: number
  usageYagura: number
  usageHoko: number
  usageAsari: number
}

export default defineComponent({
  name: 'BukiUsageRuleStageTable',
  components: { BukiWinRateRuleHistoryChart },
  props: {
    buki: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const t = useI18n()
    const store = useStore()

    const seasonEnvironments = computed(() => {
      return store.getters['battleEnvironment/getSeasonEnvironments']() as BattleEnvironment[]
    })
    
    const rules = computed((): BattleRule[] => {
      const allBattles = seasonEnvironments.value.map(env => env.battles).flat()
      return Array.from(new Set(allBattles.map(b => b.rule)))
    })
    
    const stages = computed((): BattleStage[] => {
      if (seasonEnvironments.value === undefined) {
        return []
      }
      const allBattles = seasonEnvironments.value.map(env => env.battles).flat()
      const stages = Array.from(new Set(allBattles.map(b => b.stage)))
      stages.sort((a, b) => t.t(`battleStage.${a}`) <t.t(`battleStage.${b}`)  ? -1 : 1)
      return stages
    })
    
    const items = computed((): BukiItem[] => {
      if (seasonEnvironments.value === undefined) {
        return []
      }

      const allEnvs = seasonEnvironments.value.map(env => env.bukiEnvironments).flat()
      const allBattles = seasonEnvironments.value.map(env => env.battles).flat()
      const buki = props.buki as MainWeapon
      
      const _items: BukiItem[] = []
      stages.value.forEach((stage, idx) => {
        const usageNawabari = calcWinRate(allEnvs, 'nawabari', stage, buki)
        const usageArea = calcWinRate(allEnvs, 'area', stage, buki)
        const usageYagura = calcWinRate(allEnvs, 'yagura', stage, buki)
        const usageHoko = calcWinRate(allEnvs, 'hoko', stage, buki)
        const usageAsari = calcWinRate(allEnvs, 'asari', stage, buki)
        _items.push({
          stage: stage,
          usageNawabari: calcWinRate(allEnvs, 'nawabari', stage, buki),
          usageArea: calcWinRate(allEnvs, 'area', stage, buki),
          usageYagura: calcWinRate(allEnvs, 'yagura', stage, buki),
          usageHoko: calcWinRate(allEnvs, 'hoko', stage, buki),
          usageAsari: calcWinRate(allEnvs, 'asari', stage, buki),
        })
      })
      _items.sort((a, b) => t.t(`battleStage.${a.stage}`) <t.t(`battleStage.${b.stage}`)  ? -1 : 1)
      return _items
    })

    const columns: QTableColumn[] = [
      { name: 'number', label: 'No.', field: 'number', align: 'left', sortable: false },
      { name: 'stage', label: t.t('general.stage'), field: 'stage', align: 'left', sortable: true },
      { name: 'usageArea', label: t.t('battleRule.area'), field: 'usageArea', align: 'left', sortable: true },
      { name: 'usageHoko', label: t.t('battleRule.hoko'), field: 'usageHoko', align: 'left', sortable: true },
      { name: 'usageYagura', label: t.t('battleRule.yagura'), field: 'usageYagura', align: 'left', sortable: true },
      { name: 'usageAsari', label: t.t('battleRule.asari'), field: 'usageAsari', align: 'left', sortable: true },
      { name: 'usageNawabari', label: t.t('battleRule.nawabari'), field: 'usageNawabari', align: 'left', sortable: true },
      { name: 'historyRule', label: t.t('environment.bukiUsage.usageHistory'), field: '', align: 'left'},
    ]
    
    const rateView = (rate: number): string => {
      return `${round(rate * 100, 10)}%`
    }

    return {
      columns,
      items,
      rules,
      rateView,
    }
  }
})
</script>

<style scoped>
.link {
  cursor: pointer;
}
.link:hover {
  background-color: var(--q-secondary);
}
.selected {
  background-color: rgba(0, 0, 0, 0.2);
}
.noPaddingX {
  padding-left: 0 !important;
  padding-right: 0 !important;
}
.bukiColor {
  display: inline-block;
  width: 10px;
  height: 10px;
  background-color: red;
}
</style>