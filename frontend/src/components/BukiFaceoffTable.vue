<template>
  <q-table
    flat bordered
    class="full-width q-my-md cst-sticky-header "
    align="left"
    :rows="items"
    :columns="columns"
    :hide-pagination="true"
    :pagination="{rowsPerPage: 1000}"
    :no-data-label="$t('statistics.bukiStatistics.noData')"
    row-key="bukiName"
  >
    <template v-slot:header="props">
      <q-tr :props="props">
        <q-th
          v-for="col, idx in props.cols"
          :ref="col.name"
          :key="col.name"
          :props="props"
        >
          <span v-if="col.name != 'deathBreakdown'">{{ col.label }}</span>
          <div v-else>
            <div>{{ col.label }}</div>
            <div>{{ `${$t('general.main_weapon')} / ${$t('general.sub_weapon')} / ${$t('general.sp_weapon')}` }}</div>
          </div> 
        </q-th>
      </q-tr>
    </template>
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="bukiName">
          {{ $t(`buki.main.${props.row.bukiId}`) }}
        </q-td>
        <q-td key="battleCount" :props="props">
          {{ props.row.battleCount }}
        </q-td>
        <q-td key="killRate" :props="props">
          {{ props.row.killRate === Infinity ? 'Max' : `${Math.round(props.row.killRate * 10) / 10}` }}
        </q-td>
        <q-td key="killAve" :props="props">
          {{ `${Math.round(props.row.killAve * 10) / 10}` }}
        </q-td>
        <q-td key="deathAve" :props="props">
          {{ `${Math.round(props.row.deathAve * 10) / 10}` }}
        </q-td>
        <q-td key="killTotal" :props="props">
          {{ props.row.killTotal }}
        </q-td>
        <q-td key="deathTotal" :props="props">
          {{ props.row.deathTotal }}
        </q-td>
        <q-td key="deathBreakdown" :props="props">
          <div>{{ `${props.row.deathBreakdown.deathMain} / ${props.row.deathBreakdown.deathSub} / ${props.row.deathBreakdown.deathSp}` }}</div>
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
import type { BattleStatistics } from '@/modules/BattleStatisticsApi'

interface FaceoffItem {
  bukiId: string
  killRate: number
  killAve: number
  killTotal: number
  killBreakdown: {
    killMain: number
    killSub: number
    killSp: number
  }
  deathAve: number
  deathTotal: number
  deathBreakdown: {
    deathMain: number
    deathSub: number
    deathSp: number
  }
  battleCount: number
}

export default defineComponent({
  name: 'BukiFaceoffTable',
  components: {},
  props: {
    userId: {
      type: String,
      required: true
    },
    statisticsId: {
      type: String,
      required: true
    },
    bukiId: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const t = useI18n()
    const store = useStore()
    const router = useRouter()

    const bukiId = ref()
    const battleCount = ref()
    const winRate = ref()
    const winCount = ref()
    const loseCount = ref()
    const killAve = ref()
    const deathAve = ref()
    const spAve = ref()

    const battleStatistics = computed((): BattleStatistics => {
      return store.getters['battleStatistics/getMasterStatistics'](props.userId)
    })
    
    const items = computed((): FaceoffItem[] => {
      const statistics = battleStatistics.value
      if (statistics === undefined) {
        return []
      }

      const bukiMap: {[key:string]:FaceoffItem} = {}
      statistics.bukiPerformances.forEach(perf => {
        if (props.bukiId !== perf.buki) {
          return
        }
        perf.faceoffs.forEach(faceoff => {
          if (faceoff.faceoffBuki === 'unknown') {
            return
          }
          if (bukiMap[faceoff.faceoffBuki] === undefined) {
            bukiMap[faceoff.faceoffBuki] = {
              bukiId: faceoff.faceoffBuki,
              killRate: 0,
              killAve: 0,
              killTotal: 0,
              killBreakdown: {
                killMain: 0, 
                killSub: 0,
                killSp: 0
              },
              deathAve: 0,
              deathTotal: 0,
              deathBreakdown: {
                deathMain: 0,
                deathSub: 0,
                deathSp: 0
              },
              battleCount: 0
            }
          }
          const faceoffItem = bukiMap[faceoff.faceoffBuki]
          faceoffItem.killBreakdown.killMain += faceoff.performance.killMain
          faceoffItem.killBreakdown.killSub += faceoff.performance.killSub
          faceoffItem.killBreakdown.killSp += faceoff.performance.killSp
          faceoffItem.deathBreakdown.deathMain += faceoff.performance.deathMain
          faceoffItem.deathBreakdown.deathSub += faceoff.performance.deathSub
          faceoffItem.deathBreakdown.deathSp += faceoff.performance.deathSp
          faceoffItem.battleCount += faceoff.performance.battleCount
        })
      })

      const items = Object.values(bukiMap)
      items.forEach(item => {
        item.killTotal = item.killBreakdown.killMain + item.killBreakdown.killSub + item.killBreakdown.killSp
        item.deathTotal = item.deathBreakdown.deathMain + item.deathBreakdown.deathSub + item.deathBreakdown.deathSp
        item.killRate = item.deathTotal > 0 ? item.killTotal / item.deathTotal : Infinity
        if (item.battleCount > 0) {
          item.killAve = item.killTotal / item.battleCount
          item.deathAve = item.deathTotal / item.battleCount
        }
      })

      return items
    })

    const columns: QTableColumn[] = [
      { name: 'bukiName', label: t.t('statistics.bukiStatistics.bukiName'), field: 'bukiId', align: 'left', sortable: true },
      { name: 'battleCount', label: t.t('statistics.sammary.allBattleCount'), field: 'battleCount', align: 'left', sortable: true },
      { name: 'killRate', label: t.t('statistics.sammary.killRate'), field: 'killRate', align: 'left', sortable: true },
      { name: 'killAve', label: t.t('statistics.sammary.killAve'), field: 'killAve', align: 'left', sortable: true },
      { name: 'deathAve', label: t.t('statistics.sammary.deathAve'), field: 'deathAve', align: 'left', sortable: true },
      { name: 'killTotal', label: t.t('statistics.sammary.killTotal'), field: 'killTotal', align: 'left', sortable: true },
      { name: 'deathTotal', label: t.t('statistics.sammary.deathTotal'), field: 'deathTotal', align: 'left', sortable: true },
      { name: 'deathBreakdown', label: t.t('statistics.sammary.deathBreakdown'), field: 'deathBreakdown', align: 'left', sortable: false },
    ]

    return {
      bukiId,
      battleCount,
      winRate,
      winCount,
      loseCount,
      killAve,
      deathAve,
      spAve,
      columns,
      items,
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