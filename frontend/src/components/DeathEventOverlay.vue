<template>
  <ChartOverlay :area="area">
    <template v-slot:content>
      <q-icon class="absolute" ref="" v-for="evt in deathEvents" name="highlight_off" color="red" :style="makeIconStyle(evt, eventArea)"/>
    </template>
  </ChartOverlay>
 </template>
    
<script lang="ts">
import { defineComponent, computed, watch, toRef, type PropType, type StyleValue } from 'vue'
import type { AnalysisResult, DeathEvent } from '@/modules/AnalysisResultApi'
import { remToPt } from '@/modules/Utils'
import ChartOverlay from '@/components/ChartOverlay.vue'

export default defineComponent({
  name: 'DeathEventOverlay',
  components: { ChartOverlay },
  props: {
    result: {
      type: Object as PropType<AnalysisResult>,
      required: true
    },
    area: {
      type: Array as PropType<Array<number>>,
        required: true
    },
    iconSizeRem: {
      type: Number,
      default: 2
    }
  },
  setup(props) {
    const eventArea = toRef(props.area)

    watch(() => props.area, () => {
      eventArea.value = props.area
    })
    
    const makeIconStyle = (evt: DeathEvent, area: number[]): StyleValue => {
      const iconSize = remToPt(props.iconSizeRem)
      const [left, right, top, bottom] = area
      const battleFrames = props.result.battleEndFrame - props.result.battleOpenFrame
      const localStartFrame = evt.startFrame - props.result.battleOpenFrame
      const x = (right - left) * (localStartFrame / battleFrames) - iconSize / 2
      const y = (bottom + top) / 2 - top - iconSize / 2
      return {
        left: `${x}px`,
        top: `${y}px`,
        fontSize: `${props.iconSizeRem}rem`
      }
    }

    const deathEvents = computed(() => {
      const playerIndex = props.result.mainPlayerIndex || 0
      return props.result.deathEvents.filter(evt => evt.deathPlayerIndex === playerIndex && evt.deathPlayerSide === 'team')
    })

    return {
      eventArea,
      deathEvents,
      makeIconStyle 
    }
  }
})
</script>

<style scoped>
.eventArea {
  background-color: rgba(173, 216, 230, 0.3);
}

</style>