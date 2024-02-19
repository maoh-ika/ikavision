<template>
  <div class="q-pa-xs itemContainer relative-position text-center">
    <div v-if="label" class="itemLabel">{{ label }}</div>
    <slot name="value">
      <div class="itemValue" :style="{ fontSize: valueSize }">{{ valueStr }}<span v-if="unit !== undefined" class="itemUnit">{{ unit }}</span></div>
    </slot>
    <slot name="footer" />
    <q-inner-loading :showing="value === undefined && $slots.value === undefined" />
  </div>
</template>

<script lang="ts">
import { defineComponent, watch, toRef, computed } from 'vue'

export default defineComponent({
  name: 'BattleInfo',
  components: {},
  props: {
    label: {
      type: String,
    },
    value: {
      type: String,
    },
    unit: {
      type: String
    },
    valueSize: {
      type: String
    }
  },
  setup(props) {
    const value = toRef(props.value)

    watch(() => props.value, (newValue) => {
      value.value = newValue
    })

    const valueStr = computed(() => {
      return value.value === undefined ? '-' : value.value
    })

    return {
      value,
      valueStr
    }
  }
})
</script>

<style scoped>
.itemContainer{
  color: black;
  min-width: 20%;
  width: fit-content;
}
.itemLabel {
  font-size: 1.6rem;
}
.itemValue {
  font-size: 6.4rem;
}
.itemUnit {
  font-size: 1.6rem;
}
</style>