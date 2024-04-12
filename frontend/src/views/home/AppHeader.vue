<template>
  <div class="q-pa-md">
    <q-header>
      <q-toolbar class="bg-primary text-white">
        <q-btn flat @click="drawer = !drawer" round dense icon="menu" />
        <RouterLink class="q-ml-md" to="/">
          <q-avatar>
            <img src="/logo.jpeg">
          </q-avatar>
        </RouterLink>
        <q-toolbar-title style="width: 150px;">IkaVision</q-toolbar-title>
        <q-space />
        <q-btn-dropdown v-show="curMatchType === 'x_match'" auto-close flat>
          <template v-slot:label>
            <div class="row items-center no-wrap">
              <div class="text-center">
                <div class="cst-caption">
                  {{ $t('config.xMatchRate') }}
                </div>
                {{getXMatchRateLabel(curXMatchRate)}}
              </div>
            </div>
          </template>
          <q-list>
            <q-item v-for="rate in xRates" :key="rate.id" dense clickable @click="() => setXMatchRate(rate.id as EnvironmentXMatchRate)">
              <q-item-section>
                <q-item-label>{{ rate.label }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
        <q-btn-dropdown auto-close flat>
          <template v-slot:label>
            <div class="row items-center no-wrap">
              <div class="text-center">
                <div class="cst-caption">
                  {{ $t('config.matchType') }}
                </div>
                {{getMatchTypeLabel(curMatchType)}}
              </div>
            </div>
          </template>
          <q-list>
            <q-item v-for="match in matchTypes" :key="match.id" dense clickable @click="() => setMatchType(match.id as EnvironmentMatchType)">
              <q-item-section>
                <q-item-label>{{ match.label }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-btn-dropdown>
      </q-toolbar>
      <q-banner v-if="showEnvChangedText" dense inline-actions class="bg-secondary text-black text-center">
        <div class="cst-description">{{ envChangedText }}</div>
        <template v-slot:action>
          <q-btn flat icon="close" @click="showEnvChangedText = false" />
        </template>
      </q-banner>
    </q-header>
    <q-drawer
      v-model="drawer"
      show-if-above

      :mini="miniState"
      @mouseover="miniState = false"
      @mouseout="miniState = true"
      mini-to-overlay

      :breakpoint="500"
      bordered
      :class="$q.dark.isActive ? 'bg-grey-9' : 'bg-grey-3'"
    >
      <q-scroll-area class="fit">
        <q-list padding>
          <RouterLink to="/">
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="home" />
              </q-item-section>

              <q-item-section>
                {{ $t('drawer.home') }}
              </q-item-section>
            </q-item>
          </RouterLink>
          
          <q-separator />
          
          <RouterLink to="/battleList">
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="list" />
              </q-item-section>
              <q-item-section>
                {{ $t('drawer.battleList') }}
              </q-item-section>
            </q-item>
          </RouterLink>
          <RouterLink to="/battleSearch">
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="search" />
              </q-item-section>
              <q-item-section>
                {{ $t('drawer.battleSearch') }}
              </q-item-section>
            </q-item>
          </RouterLink>
          <RouterLink to="/battleEnvironment">
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="hive" />
              </q-item-section>
              <q-item-section>
                {{ $t('drawer.battleEnvironment') }}
              </q-item-section>
            </q-item>
          </RouterLink>
          
          <!--
          <q-separator />

          <RouterLink :to="{ name: 'docs', params: { topic: 'what-is-ikavision'} }">
            <q-item clickable>
              <q-item-section avatar>
                <q-icon name="info" />
              </q-item-section>
              <q-item-section>
                {{ $t('drawer.docs') }}
              </q-item-section>
            </q-item>
          </RouterLink>
           -->
        </q-list>
      </q-scroll-area>
    </q-drawer>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue'
import { useQuasar } from 'quasar'
import { useStore } from 'vuex'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import type { EnvironmentMatchType, EnvironmentXMatchRate } from '@/modules/BattleEnvironmentApi'
import AccountMenu from './AccountMenu.vue'
import LoginButton from './LoginButton.vue'
import { allMatchTypes, allXMatchRates } from '@/models/Battle'

export default defineComponent({
  name: 'AppHeader',
  components: { AccountMenu, LoginButton },
  setup() {
    const $q = useQuasar()
    const store = useStore()
    const { t } = useI18n()
    const router = useRouter()
    const drawer = ref(false)
    const miniState = ref(true)
    const showEnvChangedText = ref(false)

    const isLoggedIn = computed(() => {
      return store.getters['user/isLoggedIn']
    })

    const matchTypes: {[key:string]:EnvironmentMatchType | string}[] = [
      { id: 'all', label: t('general.all') },
      ...allMatchTypes.map(m =>{ return { id: m, label: t(`matchType.${m}`) }})
    ]

    const xRates: {[key:string]:EnvironmentXMatchRate | string}[] = [
      { id: 'all', label: t('general.all') },
      ...allXMatchRates.map(m =>{ return { id: m, label: t(`xRates.${m}`) }})
    ]

    const curMatchType = computed(() => {
      return store.getters['battleEnvironment/getEnvironmentMatchType'] as EnvironmentMatchType
    })
    
    const curXMatchRate = computed(() => {
      return store.getters['battleEnvironment/getEnvironmentXMatchRate'] as EnvironmentXMatchRate
    })

    const envChangedText = computed(() => {
      let text = t('config.envChangedDesc1')
      if (curMatchType.value === 'all') {
        text += t(`config.allBattleMode`)
      } else {
        text += t(`matchType.${curMatchType.value}`)
      }
      if (curMatchType.value === 'x_match') {
        if (curXMatchRate.value === 'all') {
          text += '(' + t('config.allXMatchRate') + ')'
        } else {
          text += '(XP' + t(`xRates.${curXMatchRate.value}`) + ')'
        }
      }
      text += t('config.envChangedDesc2')
      return text
    })

    const getMatchTypeLabel = (type: EnvironmentMatchType): string => {
      return matchTypes.find(m => m.id === type)!.label
    }
    
    const getXMatchRateLabel = (rate: EnvironmentXMatchRate): string => {
      return xRates.find(m => m.id === rate)!.label
    }
    
    const setMatchType = async (type: EnvironmentMatchType) => {
      if (type !== curMatchType.value) {
        store.commit('battleEnvironment/setEnvironmentMatchType', type)
        showEnvChangedText.value = true
      }
    }
    
    const setXMatchRate = (rate: EnvironmentXMatchRate) => {
      if (rate !== curXMatchRate.value) {
        store.commit('battleEnvironment/setEnvironmentXMatchRate', rate)
        showEnvChangedText.value = true
      }
    }

    return {
      drawer,
      miniState,
      showEnvChangedText,
      isLoggedIn,
      matchTypes,
      xRates,
      curMatchType,
      curXMatchRate,
      envChangedText,
      getMatchTypeLabel,
      getXMatchRateLabel,
      setMatchType,
      setXMatchRate
    }
  }
})
</script>

<style scoped>
.connectButton {
  width: 130px;
}
.routerLink {
  text-decoration: none;
}
</style>