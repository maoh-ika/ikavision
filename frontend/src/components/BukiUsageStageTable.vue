<template>
  <q-table
    flat bordered
    class="q-my-md cst-sticky-header"
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
        <q-td :class="{link: props.expand}" key="bukiId" :props="props">
          <div class="row items-center q-pa-sm">
            <div>
              {{ $t(`buki.main.${props.row.bukiId}`) }}
            </div>
          </div>
        </q-td>
        <q-td v-for="stage, idx in columnStages" :key="`usage_${idx}`" :props="props">
          {{ round(props.row[`usage_${idx}`], 1000) }}
        </q-td>
        <q-td>
          <q-btn size="sm" flat round dense @click="props.expand = !props.expand" :icon="props.expand ? 'remove' : 'add'" />
        </q-td>
      </q-tr>
      <q-tr v-if="props.expand" :props="props">
        <q-td colspan="100%">
          <BukiUsageStageHistoryChart class="column" :buki="props.row.bukiId" :stages="columnStages" :height="320" />
        </q-td>
      </q-tr>
    </template>
  </q-table>
</template>
  
<script lang="ts">
import { defineComponent, computed, ref } from 'vue'
import { type QTableColumn, useQuasar } from 'quasar'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { calcBattleCount, calcUsageCount } from '@/modules/Environment'
import type { BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { round } from '@/modules/Utils'
import type { BattleStage } from '@/models/Battle'
import BukiUsageStageHistoryChart from '@/components/BukiUsageStageHistoryChart.vue'

interface BukiItem {
  bukiId: string
  usageNawabari: number
  usageArea: number
  usageYagura: number
  usageHoko: number
  usageAsari: number
}

export default defineComponent({
  name: 'BukiUsageStageTable',
  components: { BukiUsageStageHistoryChart },
  setup(props) {
    const t = useI18n()
    const store = useStore()
    const $q = useQuasar()

    const seasonEnvironments = computed(() => {
      return store.getters['battleEnvironment/getSeasonEnvironments']() as BattleEnvironment[]
    })

    const columnStages = computed((): BattleStage[] => {
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
      const allBukis = new Set(allEnvs.map(e => e.buki))

      const _items: BukiItem[] = []
      allBukis.forEach(buki => {
        const item: any = {}
        item.bukiId = buki
        columnStages.value.forEach((stage, idx) => {
          const count = calcBattleCount(allBattles, undefined, stage) 
          const usage = calcUsageCount(allEnvs, undefined, stage, buki)
            item[`usage_${idx}`] = count === 0 ? 0 : usage / count
        })
        _items.push(item)
      })
      _items.sort((a, b) => t.t(`buki.main.${a.bukiId}`) <t.t(`buki.main.${b.bukiId}`)  ? -1 : 1)
      return _items
    })

    const columns = computed((): QTableColumn[] => {
      const cols: QTableColumn[] = []
      cols.push({ name: 'number', label: 'No.', field: 'number', align: 'left', sortable: false })
      cols.push({ name: 'bukiId', label: t.t('general.buki'), field: 'bukiId', align: 'left', sortable: true })
      columnStages.value.forEach((stage, idx) => {
        cols.push({ name: `usage_${idx}`, label: t.t(`battleStage.${stage}`), field: `usage_${idx}`, align: 'left', sortable: true })
      })
      cols.push({ name: 'historyStage', label: t.t('environment.bukiUsage.usageHistory'), field: '', align: 'left'})
      return cols
    })

    return {
      columns,
      columnStages,
      items,
      round
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