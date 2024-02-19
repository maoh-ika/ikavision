<template>
<q-card class="q-pa-lg" bordered>
  <div v-for="cond, i in conditions">
    <div class="row items-center q-mb-sm">
      <div class="q-mr-sm">{{ `${$t('search.condition.condition')}${i + 1}.` }}</div>
      <KeyStringValueForm
        v-if="cond.valueType === 'string'"
        :prefix="cond.prefix"
        :value="cond.value"
        :postfix="cond.postfix"
        :updated="(value: string) => cond.value = value" />
      <KeyNumberRangeForm
        v-if="cond.valueType === 'numberRange'"
        :prefix="cond.prefix"
        :gteValue="cond.value[0]"
        :lteValue="cond.value[1]"
        :postfix="cond.postfix"
        :updated="(gte: number, lte: number) => { cond.value[0] = gte; cond.value[1] = lte }" />
      <KeyNumberRangeForm
        v-if="cond.valueType === 'dateRange'"
        date-mode
        :prefix="cond.prefix"
        :gteValue="cond.value[0]"
        :lteValue="cond.value[1]"
        :postfix="cond.postfix"
        :updated="(gte: number, lte: number) => { cond.value[0] = gte; cond.value[1] = lte }" />
      <KeyEnumValueForm
        v-if="cond.valueType === 'enum'"
        :prefix="cond.prefix"
        :value="cond.value"
        :postfix="cond.postfix"
        :items="cond.items"
        :labelGetter="cond.labelGetter"
        :updated="(value: string) => cond.value = value" />
      <DeathReasonForm
        v-if="cond.valueType === 'deathReason'"
        :prefix="cond.prefix"
        :reason-type="cond.value[0]"
        :reason="cond.value[1]"
        :postfix="cond.postfix"
        :items="cond.items"
        :labelGetter="cond.labelGetter"
        :updated="(reasonType: string, reason: string) => { cond.value[0] = reasonType; cond.value[1] = reason }" />
      <q-space/>
      <q-btn flat icon="delete" color="black" @click="deleteCondition(i)"/>
    </div>
  </div>
  <q-btn-dropdown auto-close flat :label="$t('search.add')">
    <q-list>
      <q-item v-for="def in formDefs" :key="def.name" dense clickable :disable="isMaxCount(def)" @click="() => addCondition(def)">
        <q-item-section>
          <q-item-label>{{ def.desc }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>
  </q-btn-dropdown>

  <q-card-actions align="right" class="bg-white text-teal">
    <q-btn flat :label="$t('search.clear')" color="black" @click="clear"/>
    <q-btn :disable="conditions.length === 0" outline :label="$t('search.search')" style="width: 100px;" color="accent" @click="search"/>
  </q-card-actions>
</q-card>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useStore } from 'vuex'
import KeyStringValueForm from './KeyStringValueForm.vue'
import KeyNumberRangeForm from './KeyNumberRangeForm.vue'
import KeyEnumValueForm from './KeyEnumValueForm.vue'
import DeathReasonForm from './DeathReasonForm.vue'
import type { SearchParams } from '@/modules/AnalysisResultIndexApi'
import type { SearchCondition } from '@/modules/BattleSearch'
import { allMatchTypes, allRules, allStages } from '@/models/Battle'
import { allMains, allSubs, allSpecials } from '@/models/Buki'

interface ConditionFormDef extends SearchCondition {
  valueType: 'string' | 'numberRange' | 'dateRange' | 'enum' | 'deathReason'
  prefix: string
  postfix: string
  desc: string
  defaultValue: any
  items?: {id:string, label:string}[]
  labelGetter?: Function
  maxCount: number
}

export default defineComponent({
  name: 'SearchConditionEditor',
  components: { KeyStringValueForm, KeyNumberRangeForm, KeyEnumValueForm, DeathReasonForm },
  props: {
    updated: {
      type: Function,
      default: () => {}
    }
  },
  setup(props) {
    const $t = useI18n()
    const store = useStore()

    const conditions = ref<ConditionFormDef[]>([])

    onMounted(() => {
      const lastConditions = store.getters['appConfig/getSearchConditions'] as ConditionFormDef[]
      conditions.value = [...lastConditions]
      if (conditions.value.length > 0) {
        search() // init with last conditions
      }
    })

    const trans = (id: string): string => {
      return $t.t(`search.condition.${id}`) 
    }
    
    const matchTypes = allMatchTypes.map(m =>{ return { id: m, label: $t.t(`matchType.${m}`) }})
    const winLose = ['win', 'lose'].map(m =>{ return { id: m, label: m.toUpperCase() }})
    const rules = allRules.map(m =>{ return { id: m, label: $t.t(`battleRule.${m}`) }})
    const stages = allStages.map(m =>{ return { id: m, label: $t.t(`battleStage.${m}`) }})
    const mains = allMains.map(m =>{ return { id: m, label: $t.t(`buki.main.${m}`) }})
    mains.sort((a, b) => a.label < b.label ? -1 : 1)
    const subs = allSubs.map(m =>{ return { id: m, label: $t.t(`buki.sub.${m}`) }})
    subs.sort((a, b) => a.label < b.label ? -1 : 1)
    const sps = allSpecials.map(m =>{ return { id: m, label: $t.t(`buki.sp.${m}`) }})
    sps.sort((a, b) => a.label < b.label ? -1 : 1)
    const today = new Date()
    const monthBefore = new Date(today)
    monthBefore.setMonth(monthBefore.getMonth() - 1)

    const labelGetter = (key: string): Function => {
      return (value: string): string => {
        return $t.t(`${key}.${value}`)
      }
    }

    const formDefs: ConditionFormDef[] = [
      { name: 'matchType', valueType: 'enum', prefix: trans('matchType.prefix'), postfix: trans('matchType.postfix'), desc: trans('matchType.desc'), items: matchTypes, defaultValue: 'regular_match', labelGetter: labelGetter('matchType'), maxCount: 1 },
      { name: 'battleResult', valueType: 'enum', prefix: trans('battleResult.prefix'), postfix: trans('battleResult.postfix'), desc: trans('battleResult.desc'), items: winLose, defaultValue: 'win', labelGetter: labelGetter('general'), maxCount: 1 },
      { name: 'battleRule', valueType: 'enum', prefix: trans('battleRule.prefix'), postfix: trans('battleRule.postfix'), desc: trans('battleRule.desc'), items: rules, defaultValue: 'nawabari', labelGetter: labelGetter('battleRule'), maxCount: 1 },
      { name: 'battleStage', valueType: 'enum', prefix: trans('battleStage.prefix'), postfix: trans('battleStage.postfix'), desc: trans('battleStage.desc'), items: stages, defaultValue: 'yunohana', labelGetter: labelGetter('battleStage'), maxCount: 1 },
      { name: 'battleDate', valueType: 'dateRange', prefix: trans('battleDate.prefix'), postfix: trans('battleDate.postfix'), desc: trans('battleDate.desc'), defaultValue: [monthBefore.getTime(), today.getTime()], maxCount: 1 },
      { name: 'mainPlayerBukiMain', valueType: 'enum', prefix: trans('mainPlayerBukiMain.prefix'), postfix: trans('mainPlayerBukiMain.postfix'), desc: trans('mainPlayerBukiMain.desc'), items: mains, defaultValue: 'wakaba_shooter', labelGetter: labelGetter('buki.main'), maxCount: 1 },
      { name: 'mainPlayerBukiSub', valueType: 'enum', prefix: trans('mainPlayerBukiSub.prefix'), postfix: trans('mainPlayerBukiSub.postfix'), desc: trans('mainPlayerBukiSub.desc'), items: subs, defaultValue: 'splash_bomb', labelGetter: labelGetter('buki.sub'), maxCount: 1 },
      { name: 'mainPlayerBukiSp', valueType: 'enum', prefix: trans('mainPlayerBukiSp.prefix'), postfix: trans('mainPlayerBukiSp.postfix'), desc: trans('mainPlayerBukiSp.desc'), items: sps, defaultValue: 'great_barrier', labelGetter: labelGetter('buki.sp'), maxCount: 1 },
      { name: 'enemyBukiMain', valueType: 'enum', prefix: trans('enemyBukiMain.prefix'), postfix: trans('enemyBukiMain.postfix'), desc: trans('enemyBukiMain.desc'), items: mains, defaultValue: 'wakaba_shooter', labelGetter: labelGetter('buki.main'), maxCount: 4 },
      { name: 'enemyBukiSub', valueType: 'enum', prefix: trans('enemyBukiSub.prefix'), postfix: trans('enemyBukiSub.postfix'), desc: trans('enemyBukiSub.desc'), items: subs, defaultValue: 'splash_bomb', labelGetter: labelGetter('buki.sub'), maxCount: 4 },
      { name: 'enemyBukiSp', valueType: 'enum', prefix: trans('enemyBukiSp.prefix'), postfix: trans('enemyBukiSp.postfix'), desc: trans('enemyBukiSp.desc'), items: sps, defaultValue: 'great_barrier', labelGetter: labelGetter('buki.sp'), maxCount: 4 },
      { name: 'teamBukiMain', valueType: 'enum', prefix: trans('teamBukiMain.prefix'), postfix: trans('teamBukiMain.postfix'), desc: trans('teamBukiMain.desc'), items: mains, defaultValue: 'wakaba_shooter', labelGetter: labelGetter('buki.main'), maxCount: 4 },
      { name: 'teamBukiSub', valueType: 'enum', prefix: trans('teamBukiSub.prefix'), postfix: trans('teamBukiSub.postfix'), desc: trans('teamBukiSub.desc'), items: subs, defaultValue: 'splash_bomb', labelGetter: labelGetter('buki.sub'), maxCount: 4 },
      { name: 'teamBukiSp', valueType: 'enum', prefix: trans('teamBukiSp.prefix'), postfix: trans('teamBukiSp.postfix'), desc: trans('teamBukiSp.desc'), items: sps, defaultValue: 'great_barrier', labelGetter: labelGetter('buki.sp'), maxCount: 4 },
      { name: 'matchRate', valueType: 'numberRange', prefix: trans('matchRate.prefix'), postfix: trans('matchRate.postfix'), desc: trans('matchRate.desc'), defaultValue: [2000, 2500], maxCount: 1 },
      { name: 'killCount', valueType: 'numberRange', prefix: trans('killCount.prefix'), postfix: trans('killCount.postfix'), desc: trans('killCount.desc'), defaultValue: [0, 0], maxCount: 1 },
      { name: 'deathCount', valueType: 'numberRange', prefix: trans('deathCount.prefix'), postfix: trans('deathCount.postfix'), desc: trans('deathCount.desc'), defaultValue: [0, 0], maxCount: 1 },
      { name: 'deathReason', valueType: 'deathReason', prefix: trans('deathReason.prefix'), postfix: trans('deathReason.postfix'), desc: trans('deathReason.desc'), defaultValue: ['main_weapon', 'any'], labelGetter: labelGetter('matchType.regular_match'), maxCount: 1 },
      { name: 'spCount', valueType: 'numberRange', prefix: trans('spCount.prefix'), postfix: trans('spCount.postfix'), desc: trans('spCount.desc'), defaultValue: [0, 0], maxCount: 1 },
//      { name: 'team', valueType: 'string', prefix: trans('team.prefix'), postfix: trans('team.postfix'), desc: trans('team.desc'), defaultValue: '', maxCount: 4 },
//      { name: 'enemy', valueType: 'string', prefix: trans('enemy.prefix'), postfix: trans('enemy.postfix'), desc: trans('enemy.desc'), defaultValue: '', maxCount: 4 },
//      { name: 'killDeadName', valueType: 'string', prefix: trans('killDeadName.prefix'), postfix: trans('killDeadName.postfix'), desc: trans('killDeadName.desc'), defaultValue: '', maxCount: 1 },
//      { name: 'deathKillerName', valueType: 'string', prefix: trans('deathKillerName.prefix'), postfix: trans('deathKillerName.postfix'), desc: trans('deathKillerName.desc'), defaultValue: '', maxCount: 1 },
      { name: 'deathTime', valueType: 'numberRange', prefix: trans('deathTime.prefix'), postfix: trans('deathTime.postfix'), desc: trans('deathTime.desc'), defaultValue: [0, 60], maxCount: 1 },
      { name: 'killTime', valueType: 'numberRange', prefix: trans('killTime.prefix'), postfix: trans('killTime.postfix'), desc: trans('killTime.desc'), defaultValue: [0, 60], maxCount: 1 },
    ]

    const makeSearchParams = (): SearchParams => {
      const searchParams: SearchParams = {
        pageSize: 0,
        pageIndex: 0
      }
      conditions.value.forEach(cond => {
        if (cond.name === 'matchType') { searchParams.matchType = cond.value }
        else if (cond.name === 'battleResult') { searchParams.battleResult = cond.value }
        else if (cond.name === 'battleRule') { searchParams.battleRule = cond.value }
        else if (cond.name === 'battleStage') { searchParams.battleStage = cond.value }
        else if (cond.name === 'battleDate') { searchParams.battleDateGte = cond.value[0]; searchParams.battleDateLte = cond.value[1] }
        else if (cond.name === 'mainPlayerBukiMain') { searchParams.mainPlayerBukiMain = cond.value }
        else if (cond.name === 'mainPlayerBukiSub') { searchParams.mainPlayerBukiSub = cond.value }
        else if (cond.name === 'mainPlayerBukiSp') { searchParams.mainPlayerBukiSp = cond.value }
        else if (cond.name === 'enemyBukiMain') {
          if (searchParams.enemyBukiMain === undefined) { searchParams.enemyBukiMain = [] }
          searchParams.enemyBukiMain.push(cond.value)
        } else if (cond.name === 'enemyBukiSub') {
          if (searchParams.enemyBukiSub === undefined) { searchParams.enemyBukiSub = [] }
          searchParams.enemyBukiSub.push(cond.value)
        } else if (cond.name === 'enemyBukiSp') {
          if (searchParams.enemyBukiSp === undefined) { searchParams.enemyBukiSp = [] }
          searchParams.enemyBukiSp.push(cond.value)
        } else if (cond.name === 'teamBukiMain') {
          if (searchParams.teamBukiMain === undefined) { searchParams.teamBukiMain = [] }
          searchParams.teamBukiMain.push(cond.value)
        } else if (cond.name === 'teamBukiSub') {
          if (searchParams.teamBukiSub === undefined) { searchParams.teamBukiSub = [] }
          searchParams.teamBukiSub.push(cond.value)
        } else if (cond.name === 'teamBukiSp') {
          if (searchParams.teamBukiSp === undefined) { searchParams.teamBukiSp = [] }
          searchParams.teamBukiSp .push(cond.value)
        }
        else if (cond.name === 'matchRate') { searchParams.matchRateGte = cond.value[0]; searchParams.matchRateLte = cond.value[1] }
        else if (cond.name === 'killCount') { searchParams.killCountGte = cond.value[0]; searchParams.killCountLte = cond.value[1] }
        else if (cond.name === 'deathCount') { searchParams.deathCountGte = cond.value[0]; searchParams.deathCountLte = cond.value[1] }
        else if (cond.name === 'deathReason') {
          searchParams.deathReasonType = cond.value[0]
          searchParams.deathReason = cond.value[1] !== '' && cond.value[1] !== 'any' ? cond.value[1] : undefined
        }
        else if (cond.name === 'spCount') { searchParams.spCountGte = cond.value[0]; searchParams.spCountLte = cond.value[1] }
        else if (cond.name === 'team') {
          if (searchParams.team === undefined) { searchParams.team = [] }
          searchParams.team.push(cond.value)
        } else if (cond.name === 'enemy') {
          if (searchParams.enemy === undefined) { searchParams.enemy = [] }
          searchParams.enemy.push(cond.value)
        }
        else if (cond.name === 'deathKillerName') { searchParams.deathKillerName = cond.value }
        else if (cond.name === 'deathTime') { searchParams.deathTimeGte = cond.value[0]; searchParams.deathTimeLte = cond.value[1] }
        else if (cond.name === 'killTime') { searchParams.killTimeGte = cond.value[0]; searchParams.killTimeLte = cond.value[1] }
      })
      return searchParams
    }

    const addCondition = (def: ConditionFormDef) => {
      conditions.value.push({ ...def, value: def.defaultValue})
    }

    const deleteCondition = (idx: number) => {
      conditions.value.splice(idx, 1)
    }
    
    const clear = () => {
      conditions.value = []
    }

    const search = async () => {
      const searchParams = makeSearchParams()
      props.updated(searchParams)
      store.commit('appConfig/setSearchConditions', [...conditions.value])
    }

    const isMaxCount = (def: ConditionFormDef): boolean => {
      return def.maxCount <= conditions.value.filter(c => c.name === def.name).length
    }

    return {
      formDefs,
      conditions,
      addCondition,
      deleteCondition,
      clear,
      search,
      isMaxCount
    }
  }
})
</script>

<style scoped>
.keyBox {
  width: 140px;
  height: 40px;
}
.typeBox {
  width: 120px;
  height: 40px;
}
.valueBox {
  width: 140px;
  height: 40px;
}
.arrowBox {
  height: 55px;
}
</style>