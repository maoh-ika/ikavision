<template>
  <div class="row items-center">
    <div v-if="prefix" class="q-mr-sm">{{ prefix }}</div>
    <div
      class="q-px-sm cst-rounded-boarder cst-vertical-middle">
      <q-btn-dropdown auto-close flat :label="getReasonTypeLabel(reasonType)">
        <q-list>
          <q-item v-for="type in reasonTypes" :key="type.id" dense clickable @click="() => update(type.id, 'any')">
            <q-item-section>
              <q-item-label>{{ type.label }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </div>
    <div class="q-mx-sm">{{ $t('search.condition.deathReason.middlefix') }}</div>
    <div
      class="q-px-sm cst-rounded-boarder cst-vertical-middle">
      <q-btn-dropdown auto-close flat :label="getReasonLabel(reason)">
        <q-list>
          <q-item v-for="r in reasons" :key="r.id" dense clickable @click="() => update(reasonType, r.id)">
            <q-item-section>
              <q-item-label>{{ r.label }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
    </div>
    <div v-if="postfix" class="q-ml-sm">{{ postfix }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { allMains, allSubs, allSpecials, type MainWeapon, type SubWeapon, type SpecialWeapon } from '@/models/Buki'
import type { DeathReasonType } from '@/models/Battle'
import { sub } from '@/modules/Environment'

export default defineComponent({
  name: 'DeathReasonForm',
  components: {},
  props: {
    prefix: {
      type: String
    },
    postfix: {
      type: String
    },
    reasonType: {
      type: String,
      required: true
    },
    reason: {
      type: String,
      default: 'all'
    },
    labelGetter: {
      type: Function,
      default: () => 'label'
    },
    updated: {
      type: Function,
      default: (reasonType: string, reason: string): void => {}
    }
  },
  setup(props) {
    const $t = useI18n()
    const reasonType = ref<DeathReasonType>(props.reasonType as DeathReasonType)
    const reason = ref(props.reason)

    const reasonTypes: {[key:string]:string}[] = [
      { id: 'main_weapon', label: $t.t('search.condition.main_weapon') },
      { id: 'sub_weapon', label: $t.t('search.condition.sub_weapon') },
      { id: 'sp_weapon', label: $t.t('search.condition.sp_weapon') },
    ]

    const mains: {id:MainWeapon|'any', label:string}[] = allMains.map(m =>{ return { id: m, label: $t.t(`buki.main.${m}`) }})
    mains.sort((a, b) => a.label < b.label ? -1 : 1)
    mains.unshift({ id: 'any', label: $t.t('search.condition.any') })
    const subs: {id:SubWeapon|'any', label:string}[] = allSubs.map(m =>{ return { id: m, label: $t.t(`buki.sub.${m}`) }})
    subs.sort((a, b) => a.label < b.label ? -1 : 1)
    subs.push({ id: 'any', label: $t.t('search.condition.any') })
    const sps: {id:SpecialWeapon|'any', label:string}[] = allSpecials.map(m =>{ return { id: m, label: $t.t(`buki.sp.${m}`) }})
    sps.sort((a, b) => a.label < b.label ? -1 : 1)
    sps.push({ id: 'any', label: $t.t('search.condition.any') })

    const reasons = computed(() => {
      switch (reasonType.value) {
        case 'main_weapon': return mains
        case 'sub_weapon': return subs
        case 'sp_weapon': return sps
        default: return []
      }
    })

    const getReasonTypeLabel = (type: DeathReasonType): string => {
      return reasonTypes.find(r => r.id === type)!.label
    }
    
    const getReasonLabel = (reason: string): string => {
      switch (reasonType.value) {
        case 'main_weapon': return mains.find(r => r.id === reason)!.label
        case 'sub_weapon': return subs.find(r => r.id === reason)!.label
        case 'sp_weapon': return sps.find(r => r.id === reason)!.label
        default: return ''
      }
    }

    const update = (newType: string, newReason: string) => {
      if (reasonType.value !== newType || reason.value !== newReason) {
        reasonType.value = newType as DeathReasonType
        reason.value = newReason
        props.updated(reasonType.value, reason.value)
      }
    }

    return {
      reasonType,
      reason,
      reasonTypes,
      reasons,
      getReasonTypeLabel,
      getReasonLabel,
      update
    }
  }
})
</script>

<style scoped>
</style>