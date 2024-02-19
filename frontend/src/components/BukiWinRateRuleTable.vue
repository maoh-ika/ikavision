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
    row-key="bukiId"
    column-sort-order="da"
    binary-state-sort
  >
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="number" :props="props">
          {{ props.rowIndex + 1 }}
        </q-td>
        <q-td key="bukiId" :props="props">
          <div class="row items-center q-pa-sm">
            <div>
              {{ $t(`buki.main.${props.row.bukiId}`) }}
            </div>
          </div>
        </q-td>
        <q-td key="rateArea" :props="props" >
          {{ rateView(props.row.rateArea) }}
        </q-td>
        <q-td key="rateHoko" :props="props" >
          {{ rateView(props.row.rateHoko) }}
        </q-td>
        <q-td key="rateYagura" :props="props" >
          {{ rateView(props.row.rateYagura) }}
        </q-td>
        <q-td key="rateAsari" :props="props" >
          {{ rateView(props.row.rateAsari) }}
        </q-td>
        <q-td key="rateNawabari" :props="props" >
          {{ rateView(props.row.rateNawabari) }}
        </q-td>
        <q-td>
          <q-btn size="sm" flat round dense @click="props.expand = !props.expand" :icon="props.expand ? 'remove' : 'add'" />
        </q-td>
      </q-tr>
      <q-tr v-if="props.expand" :props="props">
        <q-td colspan="100%">
          <BukiWinRateRuleHistoryChart class="column" :buki="props.row.bukiId" :rules="rules" :height="320" />
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
import type { BattleRule } from '@/models/Battle'
import BukiWinRateRuleHistoryChart from '@/components/BukiWinRateRuleHistoryChart.vue'

interface BukiItem {
  bukiId: string
  rateNawabari: number
  rateArea: number
  rateYagura: number
  rateHoko: number
  rateAsari: number
}

export default defineComponent({
  name: 'BukiWinRateRuleTable',
  components: { BukiWinRateRuleHistoryChart },
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
    
    const items = computed((): BukiItem[] => {
      if (seasonEnvironments.value === undefined) {
        return []
      }

      const allEnvs = seasonEnvironments.value.map(env => env.bukiEnvironments).flat()
      const allBukis = new Set(allEnvs.map(e => e.buki))
      const _items: BukiItem[] = []
      allBukis.forEach(buki => {
        _items.push({
          bukiId: buki,
          rateNawabari: calcWinRate(allEnvs, 'nawabari', undefined, buki),
          rateArea: calcWinRate(allEnvs, 'area', undefined, buki),
          rateYagura: calcWinRate(allEnvs, 'yagura', undefined, buki),
          rateHoko: calcWinRate(allEnvs, 'hoko', undefined, buki),
          rateAsari: calcWinRate(allEnvs, 'asari', undefined, buki)
        })
      })
      _items.sort((a, b) => t.t(`buki.main.${a.bukiId}`) <t.t(`buki.main.${b.bukiId}`)  ? -1 : 1)
      return _items
    })

    const columns: QTableColumn[] = [
      { name: 'number', label: 'No.', field: 'number', align: 'left', sortable: false },
      { name: 'bukiId', label: t.t('general.buki'), field: 'bukiId', align: 'left', sortable: true },
      { name: 'rateArea', label: t.t('battleRule.area'), field: 'rateArea', align: 'left', sortable: true },
      { name: 'rateHoko', label: t.t('battleRule.hoko'), field: 'rateHoko', align: 'left', sortable: true },
      { name: 'rateYagura', label: t.t('battleRule.yagura'), field: 'rateYagura', align: 'left', sortable: true },
      { name: 'rateAsari', label: t.t('battleRule.asari'), field: 'rateAsari', align: 'left', sortable: true },
      { name: 'rateNawabari', label: t.t('battleRule.nawabari'), field: 'rateNawabari', align: 'left', sortable: true },
      { name: 'historyRule', label: t.t('environment.bukiWinRate.rateHistory'), field: '', align: 'left'},
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
</style>