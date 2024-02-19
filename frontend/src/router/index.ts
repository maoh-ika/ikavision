import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'
import Home from '@/views/home/Home.vue'
import AnalysisRequest from '@/views/analysis-request/AnalysisRequest.vue'
import BattleList from '@/views/battle-list/BattleList.vue'
import BattleViewer from '@/views/battle-viewer/BattleViewer.vue'
import BattleStatistics from '@/views/battle-statistics/BattleStatistics.vue'
import BukiStatisticsDetail from '@/views/buki-statistics/BukiStatisticsDetail.vue'
import RuleStatisticsDetail from '@/views/rule-statistics/RuleStatisticsDetail.vue'
import StageStatisticsDetail from '@/views/stage-statistics/StageStatisticsDetail.vue'
import BattleEnvironment from '@/views/battle-environment/BattleEnvironment.vue'
import AnalysisResultSearch from '@/views/battle-search/AnalysisResultSearch.vue'
import DocsPage from '@/views/docs/DocsPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return {
        top: 0
      }
    }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/analysisRequest',
      name: 'analysisRequest',
      component: AnalysisRequest
    },
    {
      path: '/battleList',
      name: 'battleList',
      component: BattleList,
      props: true
    },
    {
      path: '/battleViewer/:userId/:jobId/:resultId',
      name: 'battleViewer',
      component: BattleViewer,
      props: true
    },
    {
      path: '/battleSearch',
      name: 'battleSearch',
      component: AnalysisResultSearch,
      props: true
    },
    {
      path: '/battleStatistics',
      name: 'battleStatistics',
      component: BattleStatistics,
      props: true
    },
    {
      path: '/battleStatistics/buki/:bukiId',
      name: 'bukiStatistics',
      component: BukiStatisticsDetail,
      props: true
    },
    {
      path: '/battleStatistics/rule/:rule',
      name: 'ruleStatistics',
      component: RuleStatisticsDetail,
      props: true
    },
    {
      path: '/battleStatistics/stage/:stage',
      name: 'stageStatistics',
      component: StageStatisticsDetail,
      props: true
    },
    {
      path: '/battleEnvironment',
      name: 'battleEnvironment',
      component: BattleEnvironment
    },
    {
      path: '/docs/:topic',
      name: 'docs',
      component: DocsPage,
      props: true
    }
  ]
})

router.beforeEach((to, from, next) => {
  const userId = store.getters['user/getUserId']
  if (userId === undefined) {
    next({ name: 'home' })
    return
  }
  if (to.name === 'battleViewer' && (to.params.userId === undefined || to.params.jobId === undefined)) {
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
