<template>
  <div class="row items-center">
    <div v-if="prefix" class="q-mr-sm">{{ prefix }}</div>
    <div
      class="q-px-sm cst-rounded-boarder cst-vertical-middle">
      <q-btn-dropdown  auto-close flat :label="labelGetter!(value)">
        <q-list>
          <q-item v-for="item in items" :key="item.id" dense clickable @click="() => update(item.id)">
            <q-item-section>
              <q-item-label>{{ item.label }}</q-item-label>
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
    items: {
      type: Array as PropType<any[]>
    },
    labelGetter: {
      type: Function,
      default: () => 'label'
    },
    updated: {
      type: Function,
      default: (value: string): void => {}
    }
  },
  setup(props) {
    const update = (value: string) => {
      props.updated(value)
    }

    return {
      update
    }
  }
})
</script>

<style scoped>
</style>