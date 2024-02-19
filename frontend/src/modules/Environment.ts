import lodash from 'lodash'
import { CandleChart } from '@/modules/CandleChart'
import type { BattleCount, BattleEnvironment, BukiEnvironment, EnvironmentMatchType, EnvironmentXMatchRate } from '@/modules/BattleEnvironmentApi'
import type { BattleStage, BattleRule } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'
import store from '@/store'

export interface History {
    total: {x: number, y: number, startTs: number, endTs: number }[]
    daily: {x: number, y: number, startTs: number, endTs: number }[]
}

export const calcBattleCount = (battleCounts: BattleCount[], rule?: BattleRule, stage?: BattleStage): number => {
    let total = 0
    battleCounts.forEach(count => {
        if (rule && count.rule !== rule) {
            return
        }
        if (stage && count.stage !== stage) {
            return
        }
        total += count.count
    })
    return total
}

export const calcBattleCountHistory = (envs: BattleEnvironment[], rule?: BattleRule, stage?: BattleStage, ignoreEnmtyPeriod: boolean=true): History => {
    const duration = 3600000 * 24
    const countChart = new CandleChart(duration, undefined, true, false)

    envs.forEach(env => {
        const date = env.startTimestamp
        const count = calcBattleCount(env.battles, rule, stage)
        countChart.addValue({ value: count, frame: date }) 
    })

    const totalData: any[] = []
    const dailyData: any[] = []
    countChart.candles.forEach((countCandle, i) => {
        if (ignoreEnmtyPeriod && countCandle.isEmpty) {
            return
        }
        dailyData.push({ x: countCandle.startFrame, y: countCandle.sum, startTs: countCandle.startFrame, endTs: countCandle.endFrame })
        let countTotal = 0
        countChart.candles.slice(0, i + 1).forEach(c => countTotal += c.sum)
        totalData.push({ x: countCandle.startFrame, y: countTotal, startTs: countCandle.startFrame, endTs: countCandle.endFrame })
    })
    
    return {
        total: totalData,
        daily: dailyData
    }
}

export const calcUsageCount = (envs: BukiEnvironment[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    let total = 0
    envs.forEach(env => {
        if (buki && env.buki !== buki) {
            return
        }
        total += calcBattleCount(env.usage, rule, stage)
    })
    return total
}

export const calcUsageCountHistory = (envs: BattleEnvironment[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon, ignoreEnmtyPeriod: boolean=true): History => {
    const duration = 3600000 * 24
    const countChart = new CandleChart(duration, undefined, true, false)

    envs.forEach(env => {
        const date = env.startTimestamp
        const count = calcUsageCount(env.bukiEnvironments, rule, stage, buki)
        countChart.addValue({ value: count, frame: date }) 
    })

    const totalData: any[] = []
    const dailyData: any[] = []
    countChart.candles.forEach((countCandle, i) => {
        if (ignoreEnmtyPeriod && countCandle.isEmpty) {
            return
        }
        dailyData.push({ x: countCandle.startFrame, y: countCandle.sum, startTs: countCandle.startFrame, endTs: countCandle.endFrame })
        let countTotal = 0
        countChart.candles.slice(0, i + 1).forEach(c => countTotal += c.sum)
        totalData.push({ x: countCandle.startFrame, y: countTotal, startTs: countCandle.startFrame, endTs: countCandle.endFrame })
    })
    
    return {
        total: totalData,
        daily: dailyData
    }
}

export const sub = (env1: BattleEnvironment, env2: BattleEnvironment): BattleEnvironment => {
    const res = lodash.cloneDeep(env1) as BattleEnvironment
    res.resultCount -= env2.resultCount
    env2.battles.forEach(battle => {
        const b = res.battles.find(b => b.rule === battle.rule && b.stage === battle.stage)
        if (b) {
            b.count -= battle.count
            if (b.count < 0) {
                b.count = 0
            }
        }
    })
    env2.bukiEnvironments.forEach(bukiEnv2 => {
        const bukiEnv1 = res.bukiEnvironments.find(b => b.buki === bukiEnv2.buki)
        if (bukiEnv1 === undefined) {
            return
        }
        bukiEnv2.results.forEach(result2 => {
            const result1 = bukiEnv1.results.find(r => r.rule === result2.rule && r.stage === result2.stage)
            if (result1) {
                result1.result.win -= result2.result.win
                if (result1.result.win < 0) {
                    result1.result.win = 0
                }
                result1.result.lose -= result2.result.lose
                if (result1.result.lose < 0) {
                    result1.result.lose = 0
                }
            }
        })
        bukiEnv2.battles.forEach(battle2 => {
            const battle1 = bukiEnv1.battles.find(b => b.rule === battle2.rule && b.stage === battle2.stage)
            if (battle1) {
                battle1.count -= battle2.count
                if (battle1.count < 0) {
                    battle1.count = 0
                }
            }
        })
        bukiEnv2.usage.forEach(usage2 => {
            const usage1 = bukiEnv1.usage.find(u => u.rule === usage2.rule && u.stage === usage2.stage)
            if (usage1) {
                usage1.count -= usage2.count
                if (usage1.count < 0) {
                    usage1.count = 0
                }
            }
        })
    })

    return res
}

export const add = (env1: BattleEnvironment, env2: BattleEnvironment): BattleEnvironment => {
    const res = lodash.cloneDeep(env1) as BattleEnvironment
    res.resultCount += env2.resultCount
    env2.battles.forEach(battle => {
        const b = res.battles.find(b => b.rule === battle.rule && b.stage === battle.stage)
        if (b) {
            b.count += battle.count
        } else {
            res.battles.push(battle)
        }
    })
    env2.bukiEnvironments.forEach(bukiEnv2 => {
        const bukiEnv1 = res.bukiEnvironments.find(b => b.buki === bukiEnv2.buki)
        if (bukiEnv1 === undefined) {
            res.bukiEnvironments.push(bukiEnv2)
            return
        }
        bukiEnv2.results.forEach(result2 => {
            const result1 = bukiEnv1.results.find(r => r.rule === result2.rule && r.stage === result2.stage)
            if (result1) {
                result1.result.win += result2.result.win
                result1.result.lose += result2.result.lose
            } else {
                bukiEnv1.results.push(result2)
            }
        })
        bukiEnv2.battles.forEach(battle2 => {
            const battle1 = bukiEnv1.battles.find(b => b.rule === battle2.rule && b.stage === battle2.stage)
            if (battle1) {
                battle1.count += battle2.count
            } else {
                bukiEnv1.battles.push(battle2)
            }
        })
        bukiEnv2.usage.forEach(usage2 => {
            const usage1 = bukiEnv1.usage.find(u => u.rule === usage2.rule && u.stage === usage2.stage)
            if (usage1) {
                usage1.count += usage2.count
            } else {
                bukiEnv2.usage.push(usage2)
            }
        })
    })

    return res
}
    
export const calcSeasonEnvironmentDaysBefore = async (
    days: number,
    fromNow: boolean = true,
    matchType?: EnvironmentMatchType,
    matchRate?: EnvironmentXMatchRate
): Promise<BattleEnvironment | undefined> => {
    matchType = matchType || store.getters['battleEnvironment/getEnvironmentMatchType']
    matchRate = matchRate || store.getters['battleEnvironment/getEnvironmentXMatchRate']
    const latest = store.getters['battleEnvironment/getSeasonEnvironments']('latest', matchType, matchRate) as BattleEnvironment[]
    if (latest.length === 0) {
        return undefined
    }
    let resEnv = latest[0]
    const today = fromNow ? new Date() : new Date(resEnv.latestBattleDate)
    const daysBefore = new Date(today)
    daysBefore.setDate(daysBefore.getDate() - (days - 1))
    const daily = store.getters['battleEnvironment/findDailyEnvironments'](daysBefore.getTime(), today.getTime()) as BattleEnvironment[]
    daily.forEach(dayEnv => resEnv = sub(resEnv, dayEnv))
    return resEnv
}
  