import { invokeApi } from './ApiGateway'
import { ApiError } from './ApiError'
import type { BattleRule, BattleStage, BattleWinLose, MatchType, DeathReasonType } from '@/models/Battle'
import type { MainWeapon, SubWeapon, SpecialWeapon, Buki } from '@/models/Buki'
import { makeBuki } from '@/modules/AnalysisResultApi'
import { toSeconds } from '@/modules/Utils'

export interface DeathEventIndex {
    deathReason: string
    reasonType: DeathReasonType
    deathTime: number
    killerName: string
}

export interface KillEventIndex {
    killTime: number
    deadName: string
}

export interface AnalysisResultIndex {
    userId: string
    resultId: string
    jobId: string
    movieFrames: number,
    frameRate: string,
    battleDate: number
    battleOpenFrame: number
    battleEndFrame: number
    resultStartFrame: number
    resultEndFrame: number
    battleDuration: number 
    battleResult: BattleWinLose 
    battleRule: BattleRule
    battleStage: BattleStage
    deathCount: number
    deathEvents: DeathEventIndex[]
    enemy: {name:string}[]
    enemyBukis: Buki[]
    enemyResultCount: number
    killCount: number
    killEvents: KillEventIndex[]
    matchRate: number
    matchType: MatchType
    spCount: number
    team: {name:string}[]
    teamBukis: Buki[]
    mainPlayerBuki: Buki
    teamResultCount: number
    mainPlayerName: string
}

export interface SearchParams {
    battleDateGte?: number
    battleDateLte?: number
    battleResult?: BattleWinLose
    battleRule?: BattleRule
    battleStage?: BattleStage
    deathCountGte?: number
    deathCountLte?: number
    deathReason?: string
    deathReasonType?: DeathReasonType
    deathKillerName?: string
    deathTimeGte?: number
    deathTimeLte?: number
    enemy?: string[]
    mainPlayerBukiMain?: MainWeapon[]
    mainPlayerBukiSub?: SubWeapon[]
    mainPlayerBukiSp?: SpecialWeapon[]
    enemyBukiMain?: MainWeapon[]
    enemyBukiSub?: SubWeapon[]
    enemyBukiSp?: SpecialWeapon[]
    enemyResultCountGte?: number
    enemyResultCountLte?: number
    killCountGte?: number
    killCountLte?: number
    killDeadName?: string
    killTimeGte?: number
    killTimeLte?: number
    matchRateGte?: number
    matchRateLte?: number
    matchType?: MatchType
    spCountGte?: number
    spCountLte?: number
    team?: string[]
    teamBukiMain?: MainWeapon[]
    teamBukiSub?: SubWeapon[]
    teamBukiSp?: SpecialWeapon[]
    pageSize: number
    pageIndex: number
}

export interface SearchResult {
    totalCount: number
    pageSize: number
    pageIndex: number
    indices: AnalysisResultIndex[]
}

const invokeAnalysisResultIndexApi = async (payload: any): Promise<any> => {
    const res = await invokeApi('/analysis_result_index', payload)
    if ('error' in res) {
        throw new ApiError(res.error)
    }
    return res
}

const makeDeathEvent = (data: any): DeathEventIndex => {
    return {
        deathReason: data.death_reason,
        reasonType: data.reason_type,
        deathTime: data.death_time,
        killerName: data.killer_name
    }
}

const makeKillEvent = (data: any): KillEventIndex => {
    return {
        killTime: data.kill_time,
        deadName: data.dead_name
    }
}

const makeIndex = (data: any): AnalysisResultIndex => {
    return {
        userId: data.user_id,
        resultId: data.result_id,
        jobId: data.job_id,
        movieFrames: data.movie_frames,
        frameRate: data.frame_rate,
        battleDate: data.battle_date * 1000,
        battleOpenFrame: data.battle_open_frame,
        battleEndFrame: data.battle_end_frame,
        resultStartFrame: data.result_end_frame,
        resultEndFrame: data.battle_date,
        battleDuration: data.battle_duration,
        battleResult: data.battle_result,
        battleRule: data.battle_rule,
        battleStage: data.battle_stage,
        deathCount: data.death_count,
        deathEvents: data.death_events.map((e: any) => makeDeathEvent(e)),
        enemy: data.enemy,
        enemyBukis: data.enemy_bukis.map((b: any) => makeBuki(b)),
        enemyResultCount: data.enemy_result_count,
        killCount: data.kill_count,
        killEvents: data.kill_events.map((e: any) => makeKillEvent(e)),
        matchRate: data.match_rate,
        matchType: data.match_type,
        spCount: data.sp_count,
        team: data.team,
        teamBukis: data.team_bukis.map((b: any) => makeBuki(b)),
        mainPlayerBuki: data.main_player_buki,
        teamResultCount: data.team_result_count,
        mainPlayerName: data.main_player_name
    }
}

export const search = async (params: SearchParams): Promise<SearchResult> => {
    const payload: any = {
        method: 'search',
        page_size: params.pageSize,
        page_index: params.pageIndex
    }
    if (params.battleDateGte !== undefined) {
        payload['battle_date_gte'] = toSeconds(params.battleDateGte)
    }
    if (params.battleDateLte !== undefined) {
        payload['battle_date_lte'] = toSeconds(params.battleDateLte)
    }
    if (params.battleResult !== undefined) {
        payload['battle_result'] = params.battleResult
    }
    if (params.battleRule !== undefined) {
        payload['battle_rule'] = params.battleRule
    }
    if (params.battleStage !== undefined) {
        payload['battle_stage'] = params.battleStage
    }
    if (params.deathCountGte !== undefined) {
        payload['death_count_gte'] = params.deathCountGte
    }
    if (params.deathCountLte !== undefined) {
        payload['death_count_lte'] = params.deathCountLte
    }
    if (params.deathReason !== undefined) {
        payload['death_reason'] = params.deathReason
    }
    if (params.deathReasonType !== undefined) {
        payload['death_reason_type'] = params.deathReasonType
    }
    if (params.deathKillerName !== undefined) {
        payload['death_killer_name'] = params.deathKillerName
    }
    if (params.deathTimeGte !== undefined) {
        payload['death_time_gte'] = params.deathTimeGte
    }
    if (params.deathTimeLte !== undefined) {
        payload['death_time_lte'] = params.deathTimeLte
    }
    if (params.enemy !== undefined) {
        payload['enemy'] = params.enemy
    }
    if (params.enemyBukiMain !== undefined) {
        payload['enemy_buki_main'] = params.enemyBukiMain
    }
    if (params.enemyBukiSub !== undefined) {
        payload['enemy_buki_sub'] = params.enemyBukiSub
    }
    if (params.enemyBukiSp !== undefined) {
        payload['enemy_buki_sp'] = params.enemyBukiSp
    }
    if (params.enemyResultCountGte !== undefined) {
        payload['enemy_result_count_gte'] = params.enemyResultCountGte
    }
    if (params.enemyResultCountLte !== undefined) {
        payload['enemy_result_count_lte'] = params.enemyResultCountLte
    }
    if (params.killCountGte !== undefined) {
        payload['kill_count_gte'] = params.killCountGte
    }
    if (params.killCountLte !== undefined) {
        payload['kill_count_lte'] = params.killCountLte
    }
    if (params.killDeadName !== undefined) {
        payload['kill_dead_name'] = params.killDeadName
    }
    if (params.killTimeGte !== undefined) {
        payload['kill_time_gte'] = params.killTimeGte
    }
    if (params.killTimeLte !== undefined) {
        payload['kill_time_lte'] = params.killTimeLte
    }
    if (params.matchRateGte !== undefined) {
        payload['match_rate_gte'] = params.matchRateGte
    }
    if (params.matchRateLte !== undefined) {
        payload['match_rate_lte'] = params.matchRateLte
    }
    if (params.matchType !== undefined) {
        payload['match_type'] = params.matchType
    }
    if (params.spCountGte !== undefined) {
        payload['sp_count_gte'] = params.spCountGte
    }
    if (params.spCountLte !== undefined) {
        payload['sp_count_lte'] = params.spCountLte
    }
    if (params.team !== undefined) {
        payload['team'] = params.team
    }
    if (params.teamBukiMain !== undefined) {
        payload['team_buki_main'] = params.teamBukiMain
    }
    if (params.teamBukiSub !== undefined) {
        payload['team_buki_sub'] = params.teamBukiSub
    }
    if (params.teamBukiSp !== undefined) {
        payload['team_buki_sp'] = params.teamBukiSp
    }
    if (params.mainPlayerBukiMain !== undefined) {
        payload['main_player_buki_main'] = params.mainPlayerBukiMain
    }
    if (params.mainPlayerBukiSub !== undefined) {
        payload['main_player_buki_sub'] = params.mainPlayerBukiSub
    }
    if (params.mainPlayerBukiSp !== undefined) {
        payload['main_player_buki_sp'] = params.mainPlayerBukiSp
    }

    const res = await invokeAnalysisResultIndexApi(payload) as any
    return {
        totalCount: res.total_count,
        pageSize: res.page_size,
        pageIndex: res.page_index,
        indices: res.indices.map((d: any) => makeIndex(d))
    }
}
