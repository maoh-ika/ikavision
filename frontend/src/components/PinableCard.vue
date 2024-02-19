<template>
  <Vue3DraggableResizable
    ref="draggable"
    :draggable="isEditing"
    :resizable="isEditing"
    @dragging="payload => onDragging(payload)"
    @resizing="payload => onResizing(payload)"
    :style="{ width: 'fit-content', height: 'fit-content' }"
  >
    <q-card :class="{ fixedRightBottom: isPinned }" :style="{ width: 'fit-content'}">
      <q-card-section class=" q-px-md q-pt-md q-pb-none row items-center no-wrap">
        <div class="text-subtitle full-width">
          <slot name="title" />
        </div>
        <q-space />
        <div class="col-auto">
          <q-btn color="grey-7" round flat icon="more_vert">
            <q-menu cover auto-close class="z-max">
              <q-list>
                <slot name="actions" />
                <q-separator />
                <div v-if="!isPinned && editEnabled">
                  <q-item v-if="!isEditing" clickable @click="() => isEditing = true">
                    <q-item-section>{{ $t('viewer.pinable.edit') }}</q-item-section>
                  </q-item>
                  <q-item v-if="isEditing" clickable @click="() => isEditing = false">
                    <q-item-section>{{ $t('viewer.pinable.editEnd') }}</q-item-section>
                  </q-item>
                </div>
                <q-item v-if="!isPinned && pinEnabled" clickable @click="() => { isPinned = true; isEditingTemp = isEditing; isEditing = false }">
                  <q-item-section>{{ $t('viewer.pinable.pin') }}</q-item-section>
                </q-item>
                <q-item v-if="isPinned" clickable @click="() => { isPinned = false; isEditing = isEditingTemp }">
                  <q-item-section>{{ $t('viewer.pinable.unpin') }}</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </div>
      </q-card-section>
      <q-card-section class="q-px-md q-pt-none">
        <slot name="content" />
      </q-card-section>
    </q-card>
  </Vue3DraggableResizable>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import Vue3DraggableResizable from 'vue3-draggable-resizable'

export default defineComponent({
  name: 'PinableCard',
  components: {
    Vue3DraggableResizable
  },
  props: {
    editable: {
      type: Boolean,
      default: false
    },
    pinned: {
      type: Boolean,
      default: false
    },
    editEnabled: {
      type: Boolean,
      default: true
    },
    pinEnabled: {
      type: Boolean,
      default: true 
    },
    onDragging: {
      type: Function,
      default: () => {}
    },
    onResizing: {
      type: Function,
      default: () => {}
    },
    onMounted: {
      type: Function,
      default: () => {}
    }
  },
  setup(props) {
    const isPinned = ref(props.pinned)
    const isEditing = ref(props.editable)
    const isEditingTemp = ref(isEditing.value)
    const draggable = ref()

    return {
      isPinned,
      isEditing,
      isEditingTemp,
      draggable
    }
  }
})
</script>

<style scoped>
.fixedRightBottom {
  position: fixed;
  bottom: 16px;
  right: 16px;
  z-index: 100;
}
</style>