<template>
  <q-table
    flat
    align="left"
    :rows="items"
    :columns="columns"
    hide-pagination
    hide-no-data
    bordered
    row-key="name"
    :table-header-style="{
      backgroundColor: teamColor,
      color: 'white'
    }"
  >
    <template v-slot:body="props">
      <q-tr :props="props">
        <q-td key="name" :props="props" class="cst-text-break" :class="{'text-bold': props.row.isMainPlayer}">
          <span>{{ props.row.name }}</span>
        </q-td>
        <q-td key="buki" :props="props" class="cst-text-break" :class="{'text-bold': props.row.isMainPlayer}">
          <div>
            {{ $t(`buki.main.${props.row.buki.main}`) }}
          </div>
          <q-separator/>
          <div>
            {{ $t(`buki.sub.${props.row.buki.sub}`) }}
          </div>
          <q-separator/>
          <div>
            {{ $t(`buki.sp.${props.row.buki.sp}`) }}
          </div>
        </q-td>
        <q-td key="kill" :props="props" class="countValue">
          {{ props.row.isMainPlayer ? props.row.kill : '-' }}
        </q-td>
        <q-td key="death" :props="props" class="countValue">
          {{ props.row.death }}
        </q-td>
        <q-td key="spTrigger" :props="props" class="countValue">
          {{ props.row.spTrigger }}
        </q-td>
      </q-tr>
    </template>
  </q-table>
</template>
  
<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import type { QTableColumn } from 'quasar'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import { toDateString } from '@/modules/Utils'
import type { AnalysisResult } from '@/modules/AnalysisResultApi'

interface MemberItem {
  name: string
  buki: {
    main: string
    sub: string
    sp: string
  }
  kill: number
  death: number
  spTrigger: number
  isMainPlayer: boolean
}

export default defineComponent({
  name: 'TeamMemberTable',
  components: { },
  props: {
    userId: {
      type: String,
      required: true
    },
    jobId: {
      type: String,
      required: true
    },
    resultId: {
      type: String,
      required: true
    },
    side: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const t = useI18n()
    const store = useStore()
    
    const analysisResult = computed((): AnalysisResult => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })

    const columns: QTableColumn[] = [
      { name: 'name', label: t.t('viewer.playerName'), field: 'name', align: 'left', sortable: true },
      { name: 'buki', label: t.t('general.buki'), field: 'buki', align: 'left', sortable: true },
      { name: 'kill', label: t.t('general.kill'), field: 'kill', align: 'left', sortable: true },
      { name: 'death', label: t.t('general.death'), field: 'death', align: 'left', sortable: true },
      { name: 'spTrigger', label: t.t('viewer.spTrriger'), field: 'spTrigger', align: 'left', sortable: true },
    ]
    
    const items = computed((): MemberItem[] => {
      const result = analysisResult.value
      if (result === undefined) {
        return []
      }

      const members = props.side === 'team' ? result.team : result.enemy
      const bukis = props.side === 'team' ? result.teamBukis : result.enemyBukis
      const items = members.map(member => {
        const buki = bukis[member.lamp_ord]
        const main = buki.mainWeapon
        const sub = buki.subWeapon
        const sp = buki.specialWeapon
        const kill = result.killEvents.filter(evt => evt.killPlayerSide === props.side && evt.killPlayerIndex === member.lamp_ord).length
        const death = result.deathEvents.filter(evt => evt.deathPlayerSide === props.side && evt.deathPlayerIndex === member.lamp_ord).length
        const spTrigger = result.specialWeaponEvents.filter(evt => evt.playerSide === props.side && evt.playerIndex === member.lamp_ord && evt.type === 'triggered').length
        const isMainPlayer = props.side === 'team' && member.side === 'team' && member.lamp_ord === result.mainPlayerIndex
        return {
          name: member.name,
          buki: {
            main,
            sub,
            sp,
          },
          kill,
          death,
          spTrigger,
          isMainPlayer
        }
      })

      return items
    })

    const teamColor = computed(() => {
      if (analysisResult.value === undefined) {
        return '#fafafa'
      }
      const color = props.side === 'team' ? analysisResult.value.teamColor : analysisResult.value.enemyColor
      return `rgb(${color.join(',')})`
    })
    
    return {
      columns,
      items,
      teamColor
    }
  }
})
</script>

<style scoped>
.tableHeader {
  color: white;
  text-shadow: -1px -1px 0 #ff5733, 1px -1px 0 #ff5733, -1px 1px 0 #ff5733, 1px 1px 0 #ff5733;
}
.countValue {
  font-size: 3.2rem;
}
</style>