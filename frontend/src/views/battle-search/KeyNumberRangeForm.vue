<template>
  <div class="row items-center">
    <div v-if="prefix" class="q-mr-sm">{{ prefix }}</div>
    <div
      class="q-px-sm cst-rounded-boarder cst-vertical-middle">
      <q-input
        v-if="dateMode"
        flat
        dense
        borderless
        type="date"
        v-model="gteValue"
        @update:model-value="updateGteDate(gteValue, lteValue)"
      />
      <q-input
        v-else
        flat
        dense
        borderless
        type="number"
        v-model.number="gteValue"
        @update:model-value="updateGte(gteValue, lteValue)"
      />
    </div>
    <div v-if="dateMode" class="q-mx-sm"> {{ $t('search.condition.gteDate') }} </div>
    <div v-else class="q-mx-sm"> {{ $t('search.condition.gte') }} </div>
    <div
      class="q-px-sm cst-rounded-boarder cst-vertical-middle">
      <q-input
        v-if="dateMode"
        flat
        dense
        borderless
        type="date"
        v-model="lteValue"
        @update:model-value="updateGteDate(gteValue, lteValue)"
      />
      <q-input
        v-else
        flat
        dense
        borderless
        type="number"
        v-model.number="lteValue"
        @update:model-value="updateLte(gteValue, lteValue)"
      />
    </div>
    <div v-if="dateMode" class="q-mx-sm">{{ $t('search.condition.lteDate') }}</div>
    <div v-else class="q-mx-sm">{{ $t('search.condition.lte') }}</div>
    <div v-if="postfix" class="q-ml-sm">{{ postfix }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import { toYYYYMMDD } from '@/modules/Utils'

export default defineComponent({
  name: 'KeyNumberRangeForm',
  components: {},
  props: {
    prefix: {
      type: String
    },
    postfix: {
      type: String
    },
    gteValue: {
      type: Number,
      default: false
    },
    lteValue: {
      type: Number,
      default: false
    },
    dateMode: {
      type: Boolean,
      default: false
    },
    updated: {
      type: Function,
      default: (gte: number, lte: number): void => {}
    }
  },
  setup(props) {
    const gteValue = props.dateMode ? ref(toYYYYMMDD(new Date(props.gteValue).getTime(), '-')) : ref(props.gteValue)
    const lteValue = props.dateMode ? ref(toYYYYMMDD(new Date(props.lteValue).getTime(), '-')) : ref(props.lteValue)
    
    watch(() => props.gteValue, newValue => {
      gteValue.value = props.dateMode ? toYYYYMMDD(new Date(newValue).getTime(), '-') : newValue
    })
    
    watch(() => props.lteValue, newValue => {
      lteValue.value = props.dateMode ? toYYYYMMDD(new Date(newValue).getTime(), '-') : newValue
    })
    
    const updateGteDate = (gte: any, lte: any) => {
      const gteDate = new Date(gte)
      gteDate.setHours(0, 0, 0, 0)
      const lteDate = new Date(lte)
      lteDate.setHours(23, 59, 59, 999)
      updateGte(gteDate.getTime(), lteDate.getTime())
    }
    
    const updateLteDate = (gte: string, lte: string) => {
      updateLte(new Date(gte).getTime(), new Date(lte).getTime())
    }

    const updateGte = (gte: any, lte: any) => {
      if (gte === '') {
        gte = 0
        gteValue.value = gte
      }
      props.updated(gte, lte)
    }
    
    const updateLte = (gte: any, lte: any) => {
      if (lte === '') {
        lte = 0
        lteValue.value = lte
      }
      props.updated(gte, lte)
    }

    return {
      gteValue,
      lteValue,
      updateGteDate,
      updateLteDate,
      updateGte,
      updateLte
    }
  }
})
</script>

<style scoped>
.keyBox {
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