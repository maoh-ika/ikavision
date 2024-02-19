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
        <q-td key="usageArea" :props="props" >
          {{ round(props.row.usageArea, 1000) }}
        </q-td>
        <q-td key="usageHoko" :props="props" >
          {{ round(props.row.usageHoko, 1000) }}
        </q-td>
        <q-td key="usageYagura" :props="props" >
          {{ round(props.row.usageYagura, 1000) }}
        </q-td>
        <q-td key="usageAsari" :props="props" >
          {{ round(props.row.usageAsari, 1000) }}
        </q-td>
        <q-td key="usageNawabari" :props="props" >
          {{ round(props.row.usageNawabari, 1000) }}
        </q-td>
        <q-td>
          <q-btn size="sm" flat round dense @click="props.expand = !props.expand" :icon="props.expand ? 'remove' : 'add'" />
        </q-td>
      </q-tr>
      <q-tr v-if="props.expand" :props="props">
        <q-td colspan="100%">
          <BukiUsageRuleHistoryChart class="column" :buki="props.row.bukiId" :rules="rules" :height="320" />
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
import { calcBattleCount, calcUsageCount } from '@/modules/Environment'
import type { BattleEnvironment } from '@/modules/BattleEnvironmentApi'
import { round } from '@/modules/Utils'
import type { BattleRule } from '@/models/Battle'
import BukiUsageRuleHistoryChart from '@/components/BukiUsageRuleHistoryChart.vue'

interface BukiItem {
  bukiId: string
  usageNawabari: number
  usageArea: number
  usageYagura: number
  usageHoko: number
  usageAsari: number
}

export default defineComponent({
  name: 'BukiUsageRuleTable',
  components: { BukiUsageRuleHistoryChart },
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
      const allBattles = seasonEnvironments.value.map(env => env.battles).flat()
      const allBukis = new Set(allEnvs.map(e => e.buki))
      const battleNawabari = calcBattleCount(allBattles, 'nawabari')
      const battleArea = calcBattleCount(allBattles, 'area')
      const battleYagura = calcBattleCount(allBattles, 'yagura')
      const battleHoko = calcBattleCount(allBattles, 'hoko')
      const battleAsari = calcBattleCount(allBattles, 'asari')
      const _items: BukiItem[] = []
      allBukis.forEach(buki => {
        const usageNawabari = calcUsageCount(allEnvs, 'nawabari', undefined, buki)
        const usageArea = calcUsageCount(allEnvs, 'area', undefined, buki)
        const usageYagura = calcUsageCount(allEnvs, 'yagura', undefined, buki)
        const usageHoko = calcUsageCount(allEnvs, 'hoko', undefined, buki)
        const usageAsari = calcUsageCount(allEnvs, 'asari', undefined, buki)
        _items.push({
          bukiId: buki,
          usageNawabari: battleNawabari === 0 ? 0 : usageNawabari / battleNawabari,
          usageArea: battleArea === 0 ? 0 : usageArea / battleArea,
          usageYagura: battleYagura === 0 ? 0 : usageYagura / battleYagura,
          usageHoko: battleHoko === 0 ? 0 : usageHoko / battleHoko,
          usageAsari: battleAsari === 0 ? 0 : usageAsari / battleAsari
        })
      })
      _items.sort((a, b) => t.t(`buki.main.${a.bukiId}`) <t.t(`buki.main.${b.bukiId}`)  ? -1 : 1)
      return _items
    })

    const columns: QTableColumn[] = [
      { name: 'number', label: 'No.', field: 'number', align: 'left', sortable: false },
      { name: 'bukiId', label: t.t('general.buki'), field: 'bukiId', align: 'left', sortable: true },
      { name: 'usageArea', label: t.t('battleRule.area'), field: 'usageArea', align: 'left', sortable: true },
      { name: 'usageHoko', label: t.t('battleRule.hoko'), field: 'usageHoko', align: 'left', sortable: true },
      { name: 'usageYagura', label: t.t('battleRule.yagura'), field: 'usageYagura', align: 'left', sortable: true },
      { name: 'usageAsari', label: t.t('battleRule.asari'), field: 'usageAsari', align: 'left', sortable: true },
      { name: 'usageNawabari', label: t.t('battleRule.nawabari'), field: 'usageNawabari', align: 'left', sortable: true },
      { name: 'historyRule', label: t.t('environment.bukiUsage.usageHistory'), field: '', align: 'left'},
    ]

    return {
      columns,
      items,
      rules,
      round,
    }
  }
})
</script>

<style scoped>
</style>