<template>
  <div class="row items-center">
    <div v-if="prefix" class="q-mr-sm">{{ prefix }}</div>
    <div
      class="q-px-sm cst-rounded-boarder cst-vertical-middle keyBox">
      <q-input
        flat
        dense
        borderless
        type="text"
        v-model="rootValue"
        lazy-rules
        @update:model-value="updated(rootValue)"
      />
    </div>
    <div v-if="postfix" class="q-ml-sm">{{ postfix }}</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

export default defineComponent({
  name: 'KeyStringValueForm',
  components: {},
  props: {
    prefix: {
      type: String
    },
    postfix: {
      type: String
    },
    value: {
      type: String,
      default: false
    },
    updated: {
      type: Function,
      default: (value: string): void => {}
    }
  },
  setup(props) {
    const rootValue = ref(props.value)

    return {
      rootValue,
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