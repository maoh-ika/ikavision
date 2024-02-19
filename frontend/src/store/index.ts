import Vuex from 'vuex'
import user from './UserStore'
import analysisJob from './AnalysisJobStore'
import analysisResult from './AnalysisResultStore'
import analysisResultIndex from './AnalysisResultIndexStore'
import appConfig from './AppConfigStore'
import battleStatistics from './BattleStatisticsStore'
import battleEnvironment from './BattleEnvironmentStore'
import debug from './DebugStore'

export default new Vuex.Store({
  modules: {
    user,
    analysisJob,
    analysisResult,
    analysisResultIndex,
    appConfig,
    battleStatistics,
    battleEnvironment,
    debug
  }
})
