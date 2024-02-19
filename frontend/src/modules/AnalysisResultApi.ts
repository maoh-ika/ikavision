import { invokeApi } from './ApiGateway'
import { ApiError } from './ApiError'
import type { BattleRule, BattleSide, BattleStage, BattleWinLose, MatchType, DeathReasonType } from '@/models/Battle'
import type { IkaPlayer } from '@/models/Player'
import type { MainWeapon, SubWeapon, SpecialWeapon, Buki } from '@/models/Buki'
import { config } from '@/modules/Config'

export interface DeathEvent {
    deathPlayerIndex: number
    deathPlayerSide: BattleSide
    killlayerIndex: number
    killlayerSide: BattleSide
    deathRrason: MainWeapon | SubWeapon | SpecialWeapon | string
    reasonType: DeathReasonType
    startFrame: number
    endFrame: number
}

export interface KillEvent {
    killPlayerIndex: number
    killPlayerSide: BattleSide
    deathPlayerIndex: number
    deathPlayerSide: BattleSide
    startFrame: number
    endFrame: number
}

export type PlayerNumberBalanceState = 
    'even' |
    'advantage' |
    'disadvantage'

export interface PlayerNumberBalanceEvent {
    teamNumber: number
    enemyNumber: number
    balanceState: PlayerNumberBalanceState
    startFrame: number
    endFrame: number
}

export interface BattleCountEvent {
    count: number
    startFrame: number
    endFrame: number
}

export type SpecialWeaponEventType =
    'fully_charged' |
    'triggered' |
    'spoiled'

export interface SpecialWeaponEvent {
    type: SpecialWeaponEventType
    playerIndex: number
    playerSide: BattleSide
    startFrame: number
    endFrame: number
}

export interface InkTankState {
    inkLevel: number
    frame: number
}

export interface AnalysisResultSammary {
    jobId: string
    userId: string
    resultId: string
    movieFrames: number
    frameRate: number
    battleDate: number
    battleOpenFrame: number
    battleEndFrame: number
    resultStartFrame: number
    resultEndFrame: number
    result: BattleWinLose
    teamResultCount?: number
    enemyResultCount?: number
    rule: BattleRule
    stage: BattleStage
    matchType: MatchType
    matchRate: number | null
    team: IkaPlayer[]
    enemy: IkaPlayer[]
    mainPlayerIndex: number
    teamColor: number[]
    enemyColor: number[]
    teamBukis: Buki[]
    enemyBukis: Buki[]
    killCount: number
    deathCount: number
    spCount: number
}

export interface AnalysisResult extends AnalysisResultSammary {
    movieName: string
    movieWidth: number
    movieHeight: number
    deathEvents: DeathEvent[]
    killEvents: KillEvent[]
    teamCountEvents?: BattleCountEvent[]
    enemyCountEvents?: BattleCountEvent[]
    playerNumberBalanceEvents: PlayerNumberBalanceEvent[]
    specialWeaponEvents: SpecialWeaponEvent[]
    inkTankStates: InkTankState[]
}

const invokeAnalysisResultApi = async (payload: any): Promise<any> => {
    const res = await invokeApi('/analysis_result', payload)
    if ('error' in res) {
        throw new ApiError(res.error)
    }
    return res
}

const invokeAnalysisResultApiPriv = async (payload: any): Promise<any> => {
    const res = await invokeApi('/analysis_result', payload, 'POST', {'X-Api-Key': config.aws.apiKey})
    if (res !== true) {
        throw new ApiError(res.error)
    }
    return res
}

export const makeBuki = (data: any): Buki => {
    return {
        mainWeapon: data.main_weapon,
        subWeapon: data.sub_weapon,
        specialWeapon: data.sp_weapon,
        subInkConsumption: data.sub_ink_consumption_percent
    }
}

const makeSammary = (data: any): AnalysisResultSammary => {
    return {
        jobId: data.job_id,
        userId: data.user_id,
        resultId: data.result_id,
        movieFrames: data.movie_frames,
        frameRate: data.frame_rate,
        battleDate: data.battle_date * 1000,
        battleOpenFrame: data.battle_open_event.start_frame,
        battleEndFrame: data.battle_end_event.end_frame,
        resultStartFrame: data.battle_result_event.start_frame,
        resultEndFrame: data.battle_result_event.end_frame,
        result: data.battle_result,
        teamResultCount: data.team_result_count,
        enemyResultCount: data.enemy_result_count,
        rule: data.battle_rule,
        stage: data.battle_stage,
        matchType: data.match_type,
        matchRate: data.match_rate,
        team: data.team.map((t: any) => {
            return {
                id: t.id,
                name: t.name,
                nickname: t.nickname,
                side: 'team',
                lamp_ord: t.lamp_ord
            }
        }),
        enemy: data.enemy.map((t: any) => {
            return {
                id: t.id,
                name: t.name,
                nickname: t.nickname,
                side: 'enemy',
                lamp_ord: t.lamp_ord
            }
        }),
        mainPlayerIndex: data.main_player_index,
        teamColor: data.team_color,
        enemyColor: data.enemy_color,
        teamBukis: data.team_bukis.map((b: any) => makeBuki(b)),
        enemyBukis: data.enemy_bukis.map((b: any) => makeBuki(b)),
        killCount: data.kill_count,
        deathCount: data.death_count,
        spCount: data.sp_count
    }
}

const makeResult = (data: any): AnalysisResult => {
    return {
        ...makeSammary(data),
        movieName: data.movie_name,
        movieWidth: data.movie_width,
        movieHeight: data.movie_height,
        deathEvents: data.death_events.map((e: any) => {
            return {
                deathPlayerIndex: e.death_player_index,
                deathPlayerSide: e.death_player_side,
                killPlayerIndex: e.kill_player_index,
                killPlayerSide: e.kill_player_side,
                deathReason: e.death_reason,
                reasonType: e.reason_type,
                startFrame: e.start_frame,
                endFrame: e.end_frame
            }
        }),
        killEvents: data.kill_events.map((e: any) => {
            return {
                killPlayerIndex: e.kill_player_index,
                killPlayerSide: e.kill_player_side,
                deathPlayerIndex: e.death_player_index,
                deathPlayerSide: e.death_player_side,
                startFrame: e.start_frame,
                endFrame: e.end_frame
            }
        }),
        playerNumberBalanceEvents: data.player_number_balance_events.map((e: any) => {
            return {
                teamNumber: e.team_number,
                enemyNumber: e.enemy_number,
                balanceState: e.balance_state,
                startFrame: e.start_frame,
                endFrame: e.end_frame
            }
        }),
        teamCountEvents: data.team_count_events?.map((e: any) => {
            return {
                count: e.count,
                startFrame: e.start_frame,
                endFrame: e.end_frame
            }
        }),
        enemyCountEvents: data.enemy_count_events?.map((e: any) => {
            return {
                count: e.count,
                startFrame: e.start_frame,
                endFrame: e.end_frame
            }
        }),
        specialWeaponEvents: data.special_weapon_events?.map((e: any) => {
            return {
                type: e.type,
                playerIndex: e.player_index,
                playerSide: e.player_side,
                startFrame: e.start_frame,
                endFrame: e.end_frame
            }
        }),
        inkTankStates: data.ink_tank_states.map((e: any) => {
            return {
                inkLevel: e.ink_level,
                frame: e.frame
            }
        })
    }
}

export const querySammaries = async (userId: string, jobIds: string[]): Promise<AnalysisResultSammary[][]> => {
    const payload = {
        method: 'query_sammaries',
        user_id: userId,
        job_ids: jobIds,
    }
    const res = await invokeAnalysisResultApi(payload) as any[][]
    return res.map(r => r.map(d => makeSammary(d)))
}

export const querySammariesPagination = async (userId: string, pageSize: number, pageToken?: any): Promise<any> => {
    const payload = {
        method: 'query_sammaries_pagination',
        user_id: userId,
        page_size: pageSize,
        page_token: pageToken,
        //order: 'asc'
    }
    const res = await invokeAnalysisResultApi(payload) as any
    return {
        sammaries: res.sammaries.map((r: any) => makeSammary(r)),
        pageToken: res.page_token
    }
}

export const getResults = async (userId: string, jobId: string): Promise<AnalysisResult[]> => {
    const payload = {
        method: 'get_results',
        user_id: userId,
        job_id: jobId
    }
    const res = await invokeAnalysisResultApi(payload) as any[]
    return res.map(r => makeResult(r))
}

export const getResult = async (userId: string, resultId: string): Promise<AnalysisResult> => {
    const payload = {
        method: 'get_result',
        user_id: userId,
        result_id: resultId
    }
    const res = await invokeAnalysisResultApi(payload) as any
    return makeResult(res)
}

export const updateResult = async (
    userId: string,
    resultId: string,
    rule?: BattleRule,
    stage?: BattleStage,
    matchType?: MatchType,
    matchRate?: number | null
): Promise<boolean> => {
    const payload = {
        method: 'update',
        user_id: userId,
        result_id: resultId,
        rule: rule,
        stage: stage,
        match_type: matchType,
        match_rate: matchRate
    }
    return await invokeAnalysisResultApiPriv(payload)
}

export const deleteResult = async (
    userId: string,
    resultId: string
): Promise<boolean> => {
    const payload = {
        method: 'delete',
        user_id: userId,
        result_id: resultId
    }
    return await invokeAnalysisResultApiPriv(payload)
}