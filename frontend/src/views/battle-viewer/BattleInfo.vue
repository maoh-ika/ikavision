<template>
  <div class="full-width column items-center justify-center">
    <div class="row full-width justify-center">
      <LabelValue label="" :value="result" style="width: 60%;">
        <template v-slot:footer>
          <div class="row justify-center items-center relative-position" :style="{height: '5rem'}">
              <div
                class="roundedLeftBar" :class="{roundedRightBar: teamCountRate === 100}"
                :style="{backgroundColor: teamColor, width: `${teamCountRate}%`}"
              />
              <div
                class="roundedRightBar" :class="{roundedLeftBar: enemyCountRate === 100}"
                :style="{backgroundColor: enemyColor, width: `${enemyCountRate}%`}"
              />
              <div class="teamCount">{{ teamCountLabel }}<span class="unit">{{ countUnit }}</span></div>
              <div class="enemyCount">{{ enemyCountLabel }}<span class="unit">{{ countUnit }}</span></div>
          </div>
        </template>
      </LabelValue>
    </div>
    <div>
      <LabelValue class="full-width q-mt-lg justify-center items-center" :label="$t('viewer.battleDate')" :value="battleDate" value-size="3.0rem" />
      <LabelValue class="full-width q-mt-lg justify-center items-center" :label="$t('general.rule')" :value="rule" value-size="3.0rem" />
      <LabelValue class="full-width q-mt-lg justify-center items-center" :label="$t('general.stage')" :value="stage" value-size="3.0rem" />
    </div>
    <div class="row full-width justify-center">
      <TeamMemberTable class="q-mt-lg memberTable" :user-id="userId" :job-id="jobId" :result-id="resultId" side="team" />
      <TeamMemberTable class="q-mt-lg memberTable" :user-id="userId" :job-id="jobId" :result-id="resultId" side="enemy" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { toYYYYMMDD } from '@/modules/Utils'
import LabelValue from '@/components/LabelValue.vue'
import TeamMemberTable from './TeamMemberTable.vue'

export default defineComponent({
  name: 'BattleInfo',
  components: { LabelValue, TeamMemberTable },
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
    }
  },
  setup(props) {
    const $q = useQuasar()
    const store = useStore()
    const { t } = useI18n()
    const isReady = ref(false)
    
    onMounted(async () => {
      try {
        $q.loading.show()
        await store.dispatch('analysisResult/fetchResult', { userId: props.userId, resultId: props.resultId })
        isReady.value = true
      } finally {
        $q.loading.hide()
      }
    })

    const analysisResult = computed(() => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })

    const battleDate = computed(() => {
      return analysisResult.value === undefined ? undefined : toYYYYMMDD(analysisResult.value.battleDate)
    })

    const result = computed(() => {
      return analysisResult.value === undefined ? undefined : analysisResult.value.result.toUpperCase()
    })

    const rule = computed(() => {
      return analysisResult.value === undefined ? undefined : t(`battleRule.${analysisResult.value.rule}`)
    })

    const stage = computed(() => {
      return analysisResult.value === undefined ? undefined : t(`battleStage.${analysisResult.value.stage}`)
    })

    const teamColor = computed(() => {
      if (analysisResult.value === undefined) {
        return '#fafafa'
      }
      return `rgb(${analysisResult.value.teamColor.join(',')})`
    })
    
    const enemyColor = computed(() => {
      if (analysisResult.value === undefined) {
        return '#fafafa'
      }
      return `rgb(${analysisResult.value.enemyColor.join(',')})`
    })

    const teamCountRate = computed(() => {
      if (
        analysisResult.value?.teamResultCount === undefined ||
        analysisResult.value?.enemyResultCount === undefined
      ) {
        return 50
      }
      if (analysisResult.value.enemyResultCount === 100) {
        return 0 // got knockout
      } else if (analysisResult.value.teamResultCount === 100) {
        return 100 // knockout
      } else {
        return analysisResult.value.teamResultCount / (analysisResult.value.teamResultCount + analysisResult.value.enemyResultCount) * 100 
      }
    })
    
    const enemyCountRate = computed(() => {
      if (
        analysisResult.value?.teamResultCount === undefined ||
        analysisResult.value?.enemyResultCount === undefined
      ) {
        return 50
      }
      if (analysisResult.value.teamResultCount === 100) {
        return 0 // got knockout
      } else if (analysisResult.value.enemyResultCount === 100) {
        return 100 // knockout
      } else {
        return analysisResult.value.enemyResultCount / (analysisResult.value.teamResultCount + analysisResult.value.enemyResultCount) * 100 
      }
    })

    const makeCountLabel = (count?: number): string => {
      return (count === undefined || count === null) ? t('viewer.analysisFailed') : count.toString()
    }

    const teamCountLabel = computed(() => {
      if (analysisResult.value === undefined) {
        return undefined
      }
      return makeCountLabel(analysisResult.value.teamResultCount)
    })
    
    const enemyCountLabel = computed(() => {
      if (analysisResult.value === undefined) {
        return undefined
      }
      return makeCountLabel(analysisResult.value.enemyResultCount)
    })
    
    const countUnit = computed(() => {
      if (analysisResult.value === undefined) {
        return ''
      }
      return analysisResult.value.rule === 'nawabari' ? '%' : t('viewer.count')
    })

    return {
      analysisResult,
      battleDate,
      result,
      rule,
      stage,
      teamColor,
      enemyColor,
      teamCountRate,
      enemyCountRate,
      teamCountLabel,
      enemyCountLabel,
      countUnit
    }
  }
})
</script>

<style scoped>
.roundedLeftBar {
  border-top-left-radius: 4px;
  border-bottom-left-radius: 4px;
  height: 100%;
}
.roundedRightBar {
  border-top-right-radius: 4px;
  border-bottom-right-radius: 4px;
  height: 100%;
}
.teamCount {
  position: absolute;
  top: 0px;
  left: 5px;
  font-size: 3.2rem;
  font-weight: bold;
  color: white;
}
.enemyCount {
  position: absolute;
  top: 0px;
  right: 5px;
  font-size: 3.2rem;
  font-weight: bold;
  color: white;
}
.unit {
  font-size: 1.0rem;
  color: white;
}
.resultLabel {
  color: var(--q-positive);
}
.memberTable {
  width: 50%;
  max-width: 640px;
  overflow: scroll;
}
@media screen and (max-width: 767px) {
  .memberTable {
    width: 80%;
    max-width: 360px;
    overflow: scroll;
  }
}
</style>