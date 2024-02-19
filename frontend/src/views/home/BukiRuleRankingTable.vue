<template>
  <div class="row justify-center tableContainer">
    <div :style="{ display: 'flex', overflow: 'scroll',  width: '90%', height: '100%' }">
      <div class="q-mx-sm q-my-lg" v-for="rule in rules" :key="rule">
        <div class="text-center"> {{ $t(`battleRule.${rule}`) }}</div>
        <q-table
          flat bordered dense
          class="cst-sticky-header"
          align="left"
          :rows="makeRanking(rule)"
          :columns="columns"
          :hide-pagination="true"
          :pagination="{rowsPerPage: 1000}"
          :no-data-label="$t('statistics.bukiStatistics.noData')"
          row-key="bukiId"
          column-sort-order="ad"
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
              <q-td key="value" :props="props">
                {{ props.row.value + valueUnit }}
              </q-td>
              <q-td key="rocIn24h" :props="props" :class="{increase: props.row.rocIn24h > 0, decrease: props.row.rocIn24h < 0}" >
                {{ `${round(props.row.rocIn24h * 100, 10)}%` }}
              </q-td>
            </q-tr>
          </template>
        </q-table>
      </div>
    </div>
  </div>
</template>
  
<script lang="ts">
import { defineComponent, computed } from 'vue'
import type { QTableColumn } from 'quasar'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { round } from '@/modules/Utils'
import type { BattleRule } from '@/models/Battle'

export interface BukiItem {
  bukiId: string
  value: string
  rocIn24h: number
}

export default defineComponent({
  name: 'BukiRuleRankingTable',
  components: {},
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
      rules.sort((a, b) => t.t(`battleRule.${a}`) < t.t(`battleRule.${b}`) ? -1 : 1)
      return rules
    })
      
    const columns: QTableColumn[] = [
      { name: 'number', label: 'No.', field: 'number', align: 'left', sortable: false , classes: 'rowItem cst-text-overflow', headerClasses: 'cst-caption'},
      { name: 'bukiId', label: t.t('general.buki'), field: 'bukiId', align: 'left', sortable: false, style: 'max-width: 150px', classes: 'rowItem cst-text-overflow', headerClasses: 'cst-caption' },
      { name: 'value', label: props.valueColumnName, field: 'value', align: 'left', sortable: true, classes: 'cst-text-overflow', headerClasses: 'cst-caption' },
      { name: 'rocIn24h', label: t.t('general.rocIn24h'), field: 'rocIn24h', align: 'left', sortable: true, classes: 'cst-text-overflow', headerClasses: 'cst-caption'},
    ]
    
    return {
      columns,
      rules,
      round,
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
  height: 300px;
}
</style>