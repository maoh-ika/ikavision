<template>
<q-card flat>
    <q-card-section class="relative-position q-pa-none" style="max-width: 320px;">
      <q-card-section class="q-pa-none">
          <img class="cursor-pointer" :src="thumbnailUrl" @click="goViewer"/>
      </q-card-section>
      <q-card-section class="q-pa-none">
        <div v-if="!isLoading">
          <div class="row">
            <q-chip v-if="isWin" class="q-mx-none" square color="accent" text-color="white" size="sm">
              <span :style="{ fontSize: '1.2rem'}">WIN</span>
            </q-chip>
            <q-chip v-if="!isWin" class="q-mx-none" square color="grey" text-color="white" size="sm">
              <span :style="{ fontSize: '1.2rem'}">LOSE</span>
            </q-chip>
            <q-chip class="q-ml-xs q-mr-none" square size="sm" :style="{ backgroundColor: matchLabelColor}">
              <span :style="{ fontSize: '1.2rem'}">{{ matchLabel }}</span>
            </q-chip>
            <q-chip square size="sm">
              <q-avatar color="primary" text-color="white" font-size="1.2rem">{{ killCount }}</q-avatar>
              {{ $t('general.kill') }}
            </q-chip>
            <q-chip square size="sm">
              <q-avatar color="primary" text-color="white" font-size="1.2rem">{{ deathCount }}</q-avatar>
              {{ $t('general.death') }}
            </q-chip>
            <q-chip square size="sm">
              <q-avatar color="primary" text-color="white" font-size="1.2rem">{{ spCount }}</q-avatar>
              SP
            </q-chip>
          </div>

          <div class="row items-center">
            <div class="cst-text-overflow col-11">{{ jobName }}</div>
            <q-icon class="col-1 cursor-pointer" name="open_in_new" @click="openSrcSite">
              <q-tooltip max-width="300px">{{ linkTooltip }}</q-tooltip>
            </q-icon>
          </div>
          <div class="row q-mt-xs items-center cst-text-overflow">
              <span class="cst-caption">{{ battleDate }}</span>
          </div>
          <div class="row q-mt-xs items-center cst-text-overflow">
              <span class="cst-caption">{{ bukiName }}</span>
              <span class="q-ml-sm cst-caption">{{ rule }}</span>
              <span class="q-ml-sm cst-caption">{{ stage }}</span>
          </div>
        </div>
      </q-card-section>
      <q-inner-loading
          :showing="isLoading"
          label-class="text-teal"
          label-style="font-size: 1.1em"
      />
    </q-card-section>
</q-card>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { BattleTimer } from '@/modules/Battle'
import type { AnalysisJob } from '@/modules/AnalysisJobApi'
import type { AnalysisResultSammary } from '@/modules/AnalysisResultApi'
import { analysisJobRequestProcessor } from '@/modules/AnalysisJobRequestProcessor'
import { toYYYYMMDDHHmmss } from '@/modules/Utils'

export default defineComponent({
  name: 'CodeTokenCard',
  components: {},
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
    },
    clicked: {
      type: Function,
      default: () => {}
    }
  },
  setup(props) {
    const store = useStore()
    const $t = useI18n()
    const router = useRouter()

    const isLoading = computed(() => {
      return analysisJob.value === undefined || analysisSammary.value === undefined
    })

    onMounted(() => {
      analysisJobRequestProcessor.add({
        userId: props.userId,
        jobId: props.jobId
      })
    })
    
    const analysisJob = computed((): AnalysisJob | undefined => {
      return store.getters['analysisJob/getJob'](props.jobId)
    })
    
    const analysisSammary = computed((): AnalysisResultSammary | undefined => {
      return store.getters['analysisResult/getSammary'](props.resultId)
    })
    
    const jobName = computed(() => {
      return analysisJob.value === undefined ? '' : analysisJob.value.jobName
    })

    const battleDate = computed(() => {
      if (analysisSammary.value === undefined) {
        return ''
      }
      return toYYYYMMDDHHmmss(analysisSammary.value.battleDate)
    })
    
    const rule = computed(() => {
      return analysisSammary.value === undefined ? '' : $t.t(`battleRule.${analysisSammary.value.rule}`)
    })
    
    const stage = computed(() => {
      return analysisSammary.value === undefined ? '' : $t.t(`battleStage.${analysisSammary.value.stage}`)
    })

    const bukiName = computed(() => {
      if (analysisSammary.value === undefined) {
        return ''
      }
      if (analysisSammary.value.mainPlayerIndex !== null && analysisSammary.value.teamBukis.length > analysisSammary.value.mainPlayerIndex) {
        return $t.t(`buki.main.${analysisSammary.value.teamBukis[analysisSammary.value.mainPlayerIndex].mainWeapon}`)
      } else {
        return 'unknown'
      }
    })

    const thumbnailUrl = computed(() => {
      return analysisJob.value === undefined ? '' : analysisJob.value.thumbnailUrl
    })

    const killCount = computed(() => {
      return analysisSammary.value === undefined ? '-' : analysisSammary.value.killCount
    })
    
    const deathCount = computed(() => {
      return analysisSammary.value === undefined ? '-' : analysisSammary.value.deathCount
    })
    
    const spCount = computed(() => {
      return analysisSammary.value === undefined ? '-' : analysisSammary.value.spCount
    })

    const isWin = computed(() => {
      return analysisSammary.value?.result === 'win'
    })

    const linkTooltip = computed(() => {
      if (analysisJob.value?.movieSource === 'youtube') {
        return $t.t('viewer.youtube')
      }
      return ''
    })

    const matchLabel = computed(() => {
      if (analysisSammary.value === undefined) {
        return '-'
      }
      if (analysisSammary.value.matchType === 'x_match') {
        if (analysisSammary.value.matchRate === null) {
          return `XP${$t.t('xRates.measurement')}`
        } else {
          return `XP${analysisSammary.value.matchRate}`
        }
      } else {
        return $t.t(`matchType.${analysisSammary.value.matchType}`)
      }
    })

    const matchLabelColor = computed(() => {
      if (analysisSammary.value === undefined) {
        return 'gray'
      }
      switch (analysisSammary.value.matchType) {
        case 'bankara_match': return '#DB702E'
        case 'fes_match': return '#DAE953'
        case 'event_match': return '#E156AD'
        case 'priv_match': return '#9A2AC7'
        case 'regular_match': return '#B4F44D'
        case 'x_match': return '#72F2A3'
        default: return 'gray'
      }
    })

    const goViewer = () => {
      router.push({ name: 'battleViewer', params: {
        userId: props.userId,
        jobId: props.jobId,
        resultId: analysisSammary.value!.resultId,
      }, query: { tab: 'analysisViewer' }})
    }

    const openSrcSite = () => {
      if (analysisSammary.value === undefined) {
        return
      }
      if (analysisJob.value?.movieSource === 'youtube') {
        const timer = new BattleTimer(analysisSammary.value)
        const url = `https://www.youtube.com/watch?v=${analysisJob.value.videoId}&t=${Math.floor(timer.battleOpenSecond)}s`
        window.open(url)
      }
    }
      
    return {
      isLoading,
      jobName,
      battleDate,
      rule,
      stage,
      bukiName,
      thumbnailUrl,
      killCount,
      deathCount,
      spCount,
      isWin,
      linkTooltip,
      matchLabel,
      matchLabelColor,
      goViewer,
      openSrcSite
    }
  }
})
</script>

<style scoped>
.winLabel {
  font-size: 2.6rem;
}
.loseLabel {
  font-size: 3.6rem;
}
</style>