import { invokeApi } from './ApiGateway'
import { ApiError } from './ApiError'
import type { MainWeapon } from '@/models/Buki'
import type { BattleStage, BattleRule } from '@/models/Battle'

export interface BattlePerformance {
    deathMain: number
    deathSp: number
    deathSub: number
    killMain: number
    killSp: number
    killSub: number
    battleCount: number
}

export interface WinLose {
    win: number
    lose: number
}

export interface BattleResult {
    rule: BattleRule
    stage: BattleStage
    result: WinLose
}

export interface BattleEvent{
    rule: BattleRule
    stage: BattleStage
    spTrigger: number
    spSpoil: number
    inkInsufficient: number
}

export interface FaceoffPerformance {
    faceoffBuki: MainWeapon
    rule: BattleRule
    stage: BattleStage
    performance: BattlePerformance
}

export interface BukiPerformance {
    buki: MainWeapon
    results: BattleResult[]
    faceoffs: FaceoffPerformance[]
    events: BattleEvent[]
}

export interface BattleStatistics {
    userId: string
    statisticsId: string
    startTimestamp: number
    endTimestamp: number
    resultCount: number
    bukiPerformances: BukiPerformance[]
}

const toBattleResults = (resResult: any): BattleResult[] => {
    const results: BattleResult[] = []
    for (const rule in resResult) {
        for (const stage in resResult[rule]) {
            const battleResult : BattleResult = {
                rule: rule as BattleRule,
                stage: stage as BattleStage,
                result: {
                    win: resResult[rule][stage].win,
                    lose: resResult[rule][stage].lose
                }
            }
            results.push(battleResult)
        }
    }
    return results
}

const toFaceoffPerformances = (resFaceoff: any): FaceoffPerformance[] => {
    const faceoffs: FaceoffPerformance[] = []
    for (const faceoffBuki in resFaceoff) {
        for (const rule in resFaceoff[faceoffBuki]) {
            for (const stage in resFaceoff[faceoffBuki][rule]) {
                const data =  resFaceoff[faceoffBuki][rule][stage]
                const faceoff: FaceoffPerformance = {
                    faceoffBuki: faceoffBuki as MainWeapon,
                    rule: rule as BattleRule,
                    stage: stage as BattleStage,
                    performance: {
                        deathMain: data.death_main,
                        deathSp: data.death_sp,
                        deathSub: data.death_sub,
                        killMain: data.kill_main,
                        killSp: data.kill_sp,
                        killSub: data.kill_sub,
                        battleCount: data.battle_count
                    }
                }
                faceoffs.push(faceoff)
            }
        }
    }
    return faceoffs
}

const toBattleEvents = (resEvents: any): BattleEvent[] => {
    const events: BattleEvent[] = []
    for (const rule in resEvents) {
        for (const stage in resEvents[rule]) {
            const data = resEvents[rule][stage]
            const battleEvent: BattleEvent = {
                rule: rule as BattleRule,
                stage: stage as BattleStage,
                spTrigger: data.sp_trigger,
                spSpoil: data.sp_spoil,
                inkInsufficient: data.ink_insufficient,
            }
            events.push(battleEvent)
        }
    }
    return events
}

const toBukiPerformances = (resBukiPerformance: any): BukiPerformance[] => {
    const performances: BukiPerformance[] = []
    for (const buki in resBukiPerformance) {
        const perform: BukiPerformance = {
            buki: buki as MainWeapon,
            results: toBattleResults(resBukiPerformance[buki].result),
            faceoffs: toFaceoffPerformances(resBukiPerformance[buki].faceoff),
            events: toBattleEvents(resBukiPerformance[buki].events)
        }
        performances.push(perform)
    }
    return performances
}

const toBattleStatistics = (res: any): BattleStatistics => {
    return {
        userId: res.user_id,
        statisticsId: res.statistics_id,
        startTimestamp: res.start_timestamp * 1000,
        endTimestamp: res.end_timestamp * 1000,
        resultCount: res.result_count,
        bukiPerformances: toBukiPerformances(res.buki_performance)
    }
}

const invokeBattleStatisticsApi = async (payload: any): Promise<any> => {
    const res = await invokeApi('/battle_statistics', payload)
    if ('error' in res) {
        throw new ApiError(res.error)
    }
    return res
}

export const getMaster = async (userId: string): Promise<BattleStatistics> => {
    const payload = {
        method: 'get_master',
        user_id: userId
    }
    const res = await invokeBattleStatisticsApi(payload)
    return toBattleStatistics(res)
}

export const getDaily = async (userId: string, startDate: number, endDate: number): Promise<BattleStatistics[]> => {
    const payload = {
        method: 'get_daily',
        user_id: userId,
        start_date: Math.round(startDate / 1000),
        end_date: Math.round(endDate / 1000)
    }
    const res = await invokeBattleStatisticsApi(payload) as any[]
    return res.map(r => toBattleStatistics(r))
}