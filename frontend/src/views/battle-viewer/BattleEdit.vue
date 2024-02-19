<template>
  <div class="full-width column items-center">
    <q-btn-dropdown class="q-my-md" color="primary" auto-close :label="$t(`matchType.${curMatchType}`)">
      <q-list>
        <q-item v-for="match in matchList" :key="match" dense clickable @click="() => selectMatchType(match)">
          <q-item-section>
            <q-item-label>{{ $t(`matchType.${match}`) }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-btn-dropdown>
    <q-btn-dropdown class="q-my-md" color="primary" auto-close :label="$t(`battleRule.${curRule}`)">
      <q-list>
        <q-item v-for="rule in ruleList" :key="rule" dense clickable @click="() => selectRule(rule)">
          <q-item-section>
            <q-item-label>{{ $t(`battleRule.${rule}`) }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-btn-dropdown>
    <q-btn-dropdown class="q-my-md" color="primary" auto-close :label="$t(`battleStage.${curStage}`)">
      <q-list>
        <q-item v-for="stage in stageList" :key="stage" dense clickable @click="() => selectStage(stage)">
          <q-item-section>
            <q-item-label>{{ $t(`battleStage.${stage}`) }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-btn-dropdown>
    <div v-if="curMatchType === 'x_match'" class="q-pa-md">
      <q-input
        v-model.number="curMatchRate"
        type="number"
        filled
        style="max-width: 200px"
      />
    </div>
    <div class="q-mt-lg text-center">
      <q-btn
        :disable="!hasUpdate"
        class=""
        color="primary"
        text-color="secondary"
        label="Update"
        no-caps
        @click="updateResult"
      />
    </div>
    <div class="q-mt-xl text-right full-width">
      <q-btn
        class="q-mt-xl"
        color="warning"
        text-color="black"
        label="Delete"
        no-caps
        @click="deleteResult"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, computed } from 'vue'
import { useQuasar } from 'quasar'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import LabelValue from '@/components/LabelValue.vue'
import TeamMemberTable from './TeamMemberTable.vue'

export default defineComponent({
  name: 'BattleEdit',
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

    const curStage = ref()
    const curRule = ref()
    const curMatchType = ref()
    const curMatchRate = ref()
    
    onMounted(async () => {
      try {
        $q.loading.show()
        await store.dispatch('analysisResult/fetchResult', { userId: props.userId, resultId: props.resultId })
        curStage.value = analysisResult.value.stage
        curRule.value = analysisResult.value.rule
        curMatchType.value = analysisResult.value.matchType
        curMatchRate.value = analysisResult.value.matchRate
        isReady.value = true
      } finally {
        $q.loading.hide()
      }
    })

    const analysisResult = computed(() => {
      return store.getters['analysisResult/getResult'](props.resultId)
    })

    const hasUpdate = computed(() => {
      if (analysisResult.value === undefined) {
        return false
      }
      return analysisResult.value.rule !== curRule.value ||
        analysisResult.value.stage !== curStage.value ||
        analysisResult.value.matchType !== curMatchType.value ||
        Math.abs(analysisResult.value.matchRate - curMatchRate.value) > 0.1 
    })

    const stageList = [
      'amabi',
      'cyouzame',
      'gonzui',
      'hirame',
      'kinmedai',
      'konbu',
      'kusaya',
      'mahimahi',
      'mantamaria',
      'masaba',
      'mategai',
      'namerou',
      'nampula',
      'sumeshi',
      'taraport',
      'yagara',
      'yunohana',
      'zatou',
      'takaashi',
      'ohyou',
      'bangaitei',
      'negitoro'
    ]

    const ruleList = computed(() => {
      if (curMatchType.value === 'regular_match' || curMatchType.value === 'fes_match') {
        return ['nawabari']
      } else {
        return [
          'area',
          'yagura',
          'hoko',
          'asari'
        ]
      }
    })

    const matchList = [
      'regular_match',
      'bankara_match',
      'x_match',
      'event_match',
      'fes_match',
      'priv_match'
    ]

    const selectRule = (rule: string) => {
      curRule.value = rule
    }
    
    const selectStage = (stage: string) => {
      curStage.value = stage
    }
    
    const selectMatchType = (type: string) => {
      curMatchType.value = type
      if (type === 'regular_match' || type === 'fes_match') {
        curRule.value = 'nawabari'
      }
    }
    
    const updateResult = async () => {
      if (!hasUpdate.value) {
        return
      }
      try {
        $q.loading.show()
        await store.dispatch('analysisResult/updateResult', {
          userId: props.userId,
          resultId: props.resultId,
          rule: curRule.value,
          stage: curStage.value,
          matchType: curMatchType.value,
          matchRate: curMatchRate.value === '' ? null: curMatchRate.value
        })
      } finally {
        $q.loading.hide()
      }
    }
    
    const deleteResult = async () => {
      try {
        $q.loading.show()
        await store.dispatch('analysisResult/deleteResult', {
          userId: props.userId,
          resultId: props.resultId,
        })
      } finally {
        $q.loading.hide()
      }
    }

    return {
      analysisResult,
      hasUpdate,
      curRule,
      curStage,
      curMatchType,
      curMatchRate,
      stageList,
      ruleList,
      matchList,
      selectRule,
      selectStage,
      selectMatchType,
      updateResult,
      deleteResult
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
</style>