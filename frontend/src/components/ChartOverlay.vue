<template>
  <div class="absolute eventArea row" :style="makeContainerStyle(eventArea)">
    <slot name="content" />
  </div>
 </template>
    
<script lang="ts">
import { defineComponent, watch, toRef, type PropType, type StyleValue } from 'vue'

export default defineComponent({
  name: 'ChartOverlay',
  components: {},
  props: {
    area: {
      type: Array as PropType<Array<number>>,
        required: true
    }
  },
  setup(props) {
    const eventArea = toRef(props.area)

    watch(() => props.area, () => {
      eventArea.value = props.area
    })
    
    const makeContainerStyle = (area: number[]): StyleValue => {
      const [left, right, top, bottom] = area
      return {
        width: `${right - left}px`,
        height: `${bottom - top}px`,
        left: `${left}px`,
        top: `${top}px`,
      }
    }

    return {
      eventArea,
      makeContainerStyle,
    }
  }
})
</script>

<style scoped>
.eventArea {
  background-color: rgba(173, 216, 230, 0.3);
}

</style>