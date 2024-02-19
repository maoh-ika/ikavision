import { invokeApi } from './ApiGateway'
import { ApiError } from './ApiError'
import type { MainWeapon } from '@/models/Buki'
import type { BattleStage, BattleRule, BattleResult, MatchType, XMatchRate } from '@/models/Battle'

export type EnvironmentMatchType = MatchType | 'all'
export type EnvironmentXMatchRate = XMatchRate | 'all'

export interface BattleCount {
    rule: BattleRule
    stage: BattleStage
    count: number
}

export interface BukiEnvironment {
    buki: MainWeapon
    results: BattleResult[]
    usage: BattleCount[]
    battles: BattleCount[]
}

export interface BattleEnvironment {
    environmentTag: string
    splatoonTitle: string
    seasonName: string
    matchType: EnvironmentMatchType
    matchRate: EnvironmentXMatchRate
    resultCount: number
    startTimestamp: number
    endTimestamp: number
    battles: BattleCount[]
    bukiEnvironments: BukiEnvironment[]
    updatedAt: number
    latestBattleDate: number
}

const toBattleResults = (resResult: any): BattleResult[] => {
    const results: BattleResult[] = []
    for (const rule in resResult) {
        for (const stage in resResult[rule]) {
            const battleResult: BattleResult = {
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

const toBattleCount = (resUsage: any): BattleCount[] => {
    const usages: BattleCount[] = []
    for (const rule in resUsage) {
        for (const stage in resUsage[rule]) {
            const usage: BattleCount = {
                rule: rule as BattleRule,
                stage: stage as BattleStage,
                count: resUsage[rule][stage]
            }
            usages.push(usage)
        }
    }
    return usages
}

const toBukiEnvironments = (resBukiEnvironment: any): BukiEnvironment[] => {
    const envs: BukiEnvironment[] = []
    for (const buki in resBukiEnvironment) {
        const env: BukiEnvironment = {
            buki: buki as MainWeapon,
            usage: toBattleCount(resBukiEnvironment[buki].usage),
            results: toBattleResults(resBukiEnvironment[buki].result),
            battles: toBattleCount(resBukiEnvironment[buki].battles)
        }
        envs.push(env)
    }
    return envs
}

const toMatchType = (envTag: string): EnvironmentMatchType => {
    // {title}_{time span}_{match type}_{match rate}
    const tokens = envTag.split('_')
    if (tokens.length < 3) {
        return 'all' // no match specified
    }
    // match type has naming rule of {type}_match
    return [tokens[2], tokens[3]].join('_') as MatchType
}

const toMatchRate = (envTag: string): EnvironmentXMatchRate => {
    // {title}_{time span}_{match type}_{match rate}
    const tokens = envTag.split('_')
    if (tokens.length < 5) {
        return 'all' // no match specified
    }
    // match rate has naming rule of {start_rate}_{end_rate}
    return [tokens[4], tokens[5]].join('_') as EnvironmentXMatchRate
}

const toBattleEnvironment= (res: any): BattleEnvironment => {
    return {
        environmentTag: res.environment_tag,
        splatoonTitle: res.splatoon_title,
        seasonName: res.season_name,
        matchType: toMatchType(res.environment_tag),
        matchRate: toMatchRate(res.environment_tag),
        resultCount: res.result_count,
        startTimestamp: res.start_timestamp * 1000,
        endTimestamp: res.end_timestamp * 1000,
        battles: toBattleCount(res.battles),
        bukiEnvironments: toBukiEnvironments(res.buki_environment),
        updatedAt: res.updated_at * 1000,
        latestBattleDate: (res.latest_battle_date || res.updated_at) * 1000
    }
}

const invokeBattleEnvironmentApi = async (payload: any): Promise<any> => {
    const res = await invokeApi('/battle_environment', payload)
    if ('error' in res) {
        throw new ApiError(res.error)
    }
    return res
}

export const querySeasons = async (splatoon_title: string): Promise<BattleEnvironment[]> => {
    const payload = {
        method: 'query_seasons',
        splatoon_title: splatoon_title
    }
    const res = await invokeBattleEnvironmentApi(payload) as any[]
    return res.map(r => toBattleEnvironment(r))
}

export const querySeasonsMatch = async (splatoon_title: string, matchType: MatchType, matchRate?: XMatchRate): Promise<BattleEnvironment[]> => {
    const payload = {
        method: 'query_seasons_match',
        splatoon_title: splatoon_title,
        match_type: matchType,
        match_rate: matchRate
    }
    const res = await invokeBattleEnvironmentApi(payload) as any[]
    return res.map(r => toBattleEnvironment(r))
}

export const querySeasonsXMatch = async (splatoon_title: string, ignoreRates: XMatchRate[]): Promise<BattleEnvironment[]> => {
    const payload = {
        method: 'query_seasons_x_match',
        splatoon_title: splatoon_title,
        ignore_rates: ignoreRates,
    }
    const res = await invokeBattleEnvironmentApi(payload) as any[]
    return res.map(r => toBattleEnvironment(r))
}

export const queryDaily = async (
    splatoon_title: string,
    startDate: number,
    endDate: number
): Promise<BattleEnvironment[]> => {
    const payload = {
        method: 'query_daily',
        splatoon_title: splatoon_title,
        start_date: Math.round(startDate / 1000),
        end_date: Math.round(endDate / 1000)
    }
    const res = await invokeBattleEnvironmentApi(payload) as BattleEnvironment[]
    return res.map(r => toBattleEnvironment(r))
}

export const queryDailyMatch = async (
    splatoon_title: string,
    startDate: number,
    endDate: number,
    matchType: MatchType,
    matchRate?: XMatchRate
): Promise<BattleEnvironment[]> => {
    const payload = {
        method: 'query_daily_match',
        splatoon_title: splatoon_title,
        start_date: Math.round(startDate / 1000),
        end_date: Math.round(endDate / 1000),
        match_type: matchType,
        match_rate: matchRate
    }
    const res = await invokeBattleEnvironmentApi(payload) as BattleEnvironment[]
    return res.map(r => toBattleEnvironment(r))
}

export const queryDailyXMatch = async (
    splatoon_title: string,
    startDate: number,
    endDate: number,
    ignoreRates?: XMatchRate[]
): Promise<BattleEnvironment[]> => {
    const payload = {
        method: 'query_daily_x_match',
        splatoon_title: splatoon_title,
        start_date: Math.round(startDate / 1000),
        end_date: Math.round(endDate / 1000),
        ignore_rates: ignoreRates
    }
    const res = await invokeBattleEnvironmentApi(payload) as BattleEnvironment[]
    return res.map(r => toBattleEnvironment(r))
}