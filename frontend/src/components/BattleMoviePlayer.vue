<template>
  <PinableCard
    :editable="false"
    :on-dragging="(payload: any) => onDragging(payload, componentName)"
    :on-resizing="(payload: any) => onResizing(payload, componentName)"
  >
    <template v-slot:title>
      {{ `${$t('viewer.movie.title')} (${battleOpenMMSS} - ${battleEndMMSS})` }}
    </template>
    <template v-slot:content>
      <video
        ref="videoPlayerElem"
        class="video-js vjs-default-skin"
        controls
        preload="auto"
        :width="width"
        :height="height"
        data-setup='{ "youtube": { "ytControls": 0, "iv_load_policy": 3, "cc_load_policy": 0 } }'
      />
    </template>
    <template v-slot:actions>
      <q-item tag="label">
        <q-option-group
          v-model="enabledActions"
          :options="actions"
          type="checkbox"
          @update:model-value="configUpdated"
        />
      </q-item>
    </template>
  </PinableCard>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import videojs from 'video.js'
import 'videojs-youtube'
import PinableCard from '@/components/PinableCard.vue'
import { BattleTimer } from '@/modules/Battle'
import type { AnalysisResult } from '@/modules/AnalysisResultApi'
import { toMMSS } from '@/modules/Utils'

const componentName = 'BattleMoviePlayer'
export default defineComponent({
  name: componentName,
  components: { PinableCard },
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
    width: {
      type: Number,
      required: true
    },
    height: {
      type: Number,
      required: true
    },
    onTimeUpdate: {
      type: Function,
      default: () => {}
    },
    onDragging: {
      type: Function,
      default: () => {}
    },
    onResizing: {
      type: Function,
      default: () => {}
    }
  },
  setup(props) {
    const store = useStore()
    const { t } = useI18n()
    const videoPlayerElem = ref()
    let videoPlayer: any = undefined
    let playTimer: any
    
    const actions = [
      { label: t('viewer.movie.playOnlyBattlePart'), value: 'playOnlyBattlePart' },
    ]
    
    const enabledActions = ref<string[]>([])
    
    watch(() => props.width, newValue => {
      videoPlayer.width(newValue)
    })
    
    watch(() => props.height, newValue => {
      videoPlayer.height(newValue)
    })
    
    const playOnlyBattlePart = computed(() => {
      return store.getters['appConfig/getPlayOnlyBattlePart']
    })

    const analysisResult = computed((): AnalysisResult => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })

    const battleOpenMMSS = computed(() => {
      return toMMSS(battleTimer.battleOpenSecond, t('general.minutes'), t('general.seconds'))
    })
    
    const battleEndMMSS = computed(() => {
      return toMMSS(battleTimer.resultEndSecond, t('general.minutes'), t('general.seconds'))
    })
    
    const battleTimer = new BattleTimer(analysisResult.value)

    onMounted(() => {
      videoPlayer = videojs(videoPlayerElem.value, {}, () => {
        videoPlayer.on('play', timeUpdateListener)
        videoPlayer.on('pause', removeTimeUpdateListener)
        videoPlayer.on('ended', removeTimeUpdateListener)
      })
      const job = store.getters['analysisJob/getJob'](props.jobId)
      videoPlayer.ready(() => {
        videoPlayer.on('loadedmetadata', () => {
          videoPlayer.currentTime(battleTimer.battleOpenSecond)
        })
      })
//      videoPlayer.on('loadedmetadata', () => {
//        videoPlayer.currentTime(battleTimer.battleOpenSecond)
//      })
      if (job.movieSource === 'youtube' ) {
        videoPlayer.src({type: 'video/youtube', src: `https://www.youtube.com/watch?v=${job.videoId}`})
      } else {
        const url = ''//await generateDownloadUrl(props.userId, props.jobId) as DownnloadUrlRes
        videoPlayer.src({type: 'video/mp4', src: url})
      }
    })

    onBeforeUnmount(() => {
      if (videoPlayer) {
        videoPlayer.dispose()
        removeTimeUpdateListener()
      }
    })

    const timeUpdateListener = () => {
      if (playTimer === undefined) {
        if (playOnlyBattlePart.value) {
          const time = videoPlayer.currentTime()
          if (time < battleTimer.battleOpenSecond) {
            videoPlayer.currentTime(battleTimer.battleOpenSecond)
          } else if (battleTimer.resultEndSecond < time)  {
            videoPlayer.currentTime(battleTimer.resultEndSecond)
          }
        }
        playTimer = window.setInterval(() => {
          const time = videoPlayer.currentTime()
          if (playOnlyBattlePart.value) {
            if (time < battleTimer.battleOpenSecond || battleTimer.resultEndSecond < time) {
              videoPlayer.pause()
            }
          }
          props.onTimeUpdate(time)
        }, 30)
      }
    }
    
    const removeTimeUpdateListener = () => {
      if (playTimer) {
        window.clearInterval(playTimer)
        playTimer = undefined
      }
    }

    const setTime = (movieTime: number) => {
      if (playTimer === undefined) {
        if (playOnlyBattlePart.value) {
          if (movieTime < battleTimer.battleOpenSecond) {
            movieTime = battleTimer.battleOpenSecond
          } else if (battleTimer.resultEndSecond < movieTime) {
            movieTime = battleTimer.resultEndSecond
          }
        }
        videoPlayer.currentTime(movieTime)
      }
    }

    const configUpdated = (value: string[]) => {
      const enabled = enabledActions.value.find(v => v === 'playOnlyBattlePart') !== undefined 
      store.commit('appConfig/setPlayOnlyBattlePart', enabled)
    }
    
    if (playOnlyBattlePart.value) {
      enabledActions.value.push('playOnlyBattlePart')
    }

    return {
      componentName,
      videoPlayerElem,
      enabledActions,
      actions,
      battleOpenMMSS,
      battleEndMMSS,
      setTime,
      configUpdated
    }
  }
})
</script>

<style >
:deep(div.ytp-pause-overlay-container) {
  display: none !important;
}
</style>