import { CandleChart } from '@/modules/CandleChart'
import { toZeroHour } from '@/modules/Utils'
import type { BattleStatistics, BukiPerformance } from '@/modules/BattleStatisticsApi'
import type { BattleStage, BattleRule, BattleResult } from '@/models/Battle'
import type { MainWeapon } from '@/models/Buki'

interface BukiResult {
    buki: MainWeapon
    results: BattleResult[]
}

interface ScopedBukiResult {
    startTimestamp: number
    endTimestamp: number
    bukiPerformances: BukiResult[]
}

export const calcWinLoseCount = (bukiResults: BukiResult[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number[] => {
    let winTotal = 0
    let loseTotal = 0
    bukiResults.forEach(perf => {
        if (buki && perf.buki !== buki) {
            return
        }
        perf.results.forEach(res => {
            if (rule && res.rule !== rule) {
                return
            }
            if (stage && res.stage !== stage) {
                return
            }
            winTotal += res.result.win
            loseTotal += res.result.lose
        })
    })
    return [winTotal, loseTotal]
}

export const calcWinRate = (bukiResults: BukiResult[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    const [winTotal, loseTotal] = calcWinLoseCount(bukiResults, rule, stage, buki)
    return (winTotal > 0 || loseTotal > 0) ? winTotal / (winTotal + loseTotal) : 0
}

export const calcBattleCount = (bukiResults: BukiResult[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    const winLose = calcWinLoseCount(bukiResults, rule, stage, buki)
    return winLose[0] + winLose[1]
}

export interface History {
    total: {x: number, y: number, startTs: number, endTs: number }[]
    daily: {x: number, y: number, startTs: number, endTs: number }[]
}

export const calcWinLoseCountHistory = (stats: ScopedBukiResult[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon, ignoreEnmtyPeriod: boolean=true): History[] => {
    const duration = 3600000 * 24
    
    const winChart = new CandleChart(duration, undefined, true, false)
    const loseChart = new CandleChart(duration, undefined, true, false)
    stats.forEach(stat => {
        const date = toZeroHour(stat.startTimestamp)
        const winLose = calcWinLoseCount(stat.bukiPerformances, rule, stage, buki)
        winChart.addValue({ value: winLose[0], frame: date }) 
        loseChart.addValue({ value: winLose[1], frame: date }) 
    })

    const winData: any[] = []
    const dailyWinData: any[] = []
    const loseData: any[] = []
    const dailyLoseData: any[] = []
    winChart.candles.forEach((winCandle, i) => {
        const loseCandle = loseChart.getCandle(i)!
        if (ignoreEnmtyPeriod && winCandle.isEmpty && loseCandle.isEmpty) {
            return
        }
        const dailyWin = winCandle.sum
        const dailyLose = loseCandle!.sum
        dailyWinData.push({ x: winCandle.startFrame, y: dailyWin})
        dailyLoseData.push({ x: loseCandle.startFrame, y: dailyLose})

        let winTotal = 0
        winChart.candles.slice(0, i + 1).forEach(c => winTotal += c.sum)
        let loseTotal = 0
        loseChart.candles.slice(0, i + 1).forEach(c => loseTotal += c.sum)
        winData.push({ x: winCandle.startFrame, y: winTotal, startTs: winCandle.startFrame, endTs: winCandle.endFrame })
        loseData.push({ x: winCandle.startFrame, y: loseTotal, startTs: winCandle.startFrame, endTs: winCandle.endFrame })
    })
    return [
        {
            total: winData,
            daily: dailyWinData
        },
        {
            total: loseData,
            daily: dailyLoseData
        }
    ]
}

export const calcWinRateHistory = (stats: ScopedBukiResult[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon, ignoreEnmtyPeriod: boolean=true): History => {
    const duration = 3600000 * 24
    
    const winChart = new CandleChart(duration, undefined, true, false)
    const loseChart = new CandleChart(duration, undefined, true, false)
    stats.forEach(stat => {
        const date = toZeroHour(stat.startTimestamp)
        const winLose = calcWinLoseCount(stat.bukiPerformances, rule, stage, buki)
        winChart.addValue({ value: winLose[0], frame: date }) 
        loseChart.addValue({ value: winLose[1], frame: date }) 
    })

    const rateData: any[] = []
    const dailyRateData: any[] = []
    winChart.candles.forEach((winCandle, i) => {
        const loseCandle = loseChart.getCandle(i)
        if (ignoreEnmtyPeriod && winCandle.isEmpty && loseCandle?.isEmpty) {
            return
        }
        const dailyWin = winCandle.sum
        const dailyLose = loseCandle!.sum
        const dailyWinRate = (dailyWin > 0 || dailyLose > 0) ? dailyWin / (dailyWin + dailyLose) : 0
        dailyRateData.push({ x: winCandle.startFrame, y: Math.round(dailyWinRate * 1000) / 10, startTs: winCandle.startFrame, endTs: winCandle.endFrame })

        let winTotal = 0
        winChart.candles.slice(0, i + 1).forEach(c => winTotal += c.sum)
        let loseTotal = 0
        loseChart.candles.slice(0, i + 1).forEach(c => loseTotal += c.sum)
        const winRate = (winTotal > 0 || loseTotal > 0) ? winTotal / (winTotal + loseTotal) : 0
        rateData.push({ x: winCandle.startFrame, y: Math.round(winRate * 1000) / 10, startTs: winCandle.startFrame, endTs: winCandle.endFrame })
    })
    return {
        total: rateData,
        daily: dailyRateData
    }
}

export const calcBattleCountHistory = (stats: ScopedBukiResult[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon, ignoreEnmtyPeriod: boolean=true): History => {
    const duration = 3600000 * 24
    const countChart = new CandleChart(duration, undefined, true, false)

    stats.forEach(stat => {
        const date = toZeroHour(stat.startTimestamp)
        const count = calcBattleCount(stat.bukiPerformances, rule, stage, buki)
        countChart.addValue({ value: count, frame: date }) 
    })

    const totalData: any[] = []
    const dailyData: any[] = []
    countChart.candles.forEach((countCandle, i) => {
        if (ignoreEnmtyPeriod && countCandle.isEmpty) {
            return
        }
        dailyData.push({ x: countCandle.startFrame, y: countCandle.sum })
        let countTotal = 0
        countChart.candles.slice(0, i + 1).forEach(c => countTotal += c.sum)
        totalData.push({ x: countCandle.startFrame, y: countTotal, startTs: countCandle.startFrame, endTs: countCandle.endFrame })
    })
    
    return {
        total: totalData,
        daily: dailyData
    }
}

export const calcKillCount = (bukiPerformances: BukiPerformance[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    let killTotal = 0
    bukiPerformances.forEach(perf => {
        if (buki && perf.buki !== buki) {
            return
        }
        perf.faceoffs.forEach(faceoff => {
            if (rule && faceoff.rule !== rule) {
                return
            }
            if (stage && faceoff.stage !== stage) {
                return
            }
            killTotal += (faceoff.performance.killMain + faceoff.performance.killSub + faceoff.performance.killSp)
        })
    })
    return killTotal
}

export const calcKillAve = (bukiPerformances: BukiPerformance[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    const total = calcKillCount(bukiPerformances, rule, stage, buki)
    const count = calcBattleCount(bukiPerformances, rule, stage, buki)
    return count > 0 ? total / count : 0
}

export const calcKillAveHistory = (stats: BattleStatistics[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon, ignoreEnmtyPeriod: boolean=true): History => {
    const duration = 3600000 * 24
    const killChart = new CandleChart(duration, undefined, true, false)
    const countChart = new CandleChart(duration, undefined, true, false)

    stats.forEach(stat => {
        const battleDate = toZeroHour(stat.startTimestamp)
        const killTotal = calcKillCount(stat.bukiPerformances, rule, stage, buki)
        const battleCount = calcBattleCount(stat.bukiPerformances, rule, stage, buki)
        killChart.addValue({ value: killTotal, frame: battleDate }) 
        countChart.addValue({ value: battleCount, frame: battleDate }) 
    })

    const totalData: any[] = []
    const dailyData: any[] = []
    countChart.candles.forEach((countCandle, i) => {
        const killCandle = killChart.getCandle(i)!
        if (ignoreEnmtyPeriod && countCandle.isEmpty) {
            return
        }
        const dailyCount = countCandle.sum
        const dailyKill = killCandle.sum
        const dailyAve = dailyKill / dailyCount
        dailyData.push({ x: countCandle.startFrame, y: dailyAve, startTs: countCandle.startFrame, endTs: countCandle.endFrame  })
        
        let countTotal = 0
        countChart.candles.slice(0, i + 1).forEach(c => countTotal += c.sum)
        let killTotal = 0
        killChart.candles.slice(0, i + 1).forEach(c => killTotal += c.sum)
        const totalAve = killTotal / countTotal
        totalData.push({ x: countCandle.startFrame, y: totalAve, startTs: countCandle.startFrame, endTs: countCandle.endFrame  })
    })
    
    return {
        total: totalData,
        daily: dailyData
    }
}

export const calcDeathCount = (bukiPerformances: BukiPerformance[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    let deathTotal = 0
    bukiPerformances.forEach(perf => {
        if (buki && perf.buki !== buki) {
            return
        }
        perf.faceoffs.forEach(faceoff => {
            if (rule && faceoff.rule !== rule) {
                return
            }
            if (stage && faceoff.stage !== stage) {
                return
            }
            deathTotal  += (faceoff.performance.deathMain + faceoff.performance.deathSub + faceoff.performance.deathSp)
        })
    })
    return deathTotal
}

export const calcDeathAve = (bukiPerformances: BukiPerformance[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    const deathTotal = calcDeathCount(bukiPerformances, rule, stage, buki)
    const count = calcBattleCount(bukiPerformances, rule, stage, buki)
    return count > 0 ? deathTotal / count : 0
}

export const calcDeathAveHistory = (stats: BattleStatistics[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon, ignoreEnmtyPeriod: boolean=true): History => {
    const duration = 3600000 * 24
    const deathChart = new CandleChart(duration, undefined, true, false)
    const countChart = new CandleChart(duration, undefined, true, false)
    
    stats.forEach(stat => {
        const battleDate = toZeroHour(stat.startTimestamp)
        const deathTotal = calcDeathCount(stat.bukiPerformances, rule, stage, buki)
        const battleCount = calcBattleCount(stat.bukiPerformances, rule, stage, buki)
        deathChart.addValue({ value: deathTotal, frame: battleDate }) 
        countChart.addValue({ value: battleCount, frame: battleDate }) 
    })

    const totalData: any[] = []
    const dailyData: any[] = []
    countChart.candles.forEach((countCandle, i) => {
        const deathCandle = deathChart.getCandle(i)!
        if (ignoreEnmtyPeriod && countCandle.isEmpty) {
            return
        }
        const dailyCount = countCandle.sum
        const dailyDeath = deathCandle.sum
        const dailyAve = dailyDeath / dailyCount
        dailyData.push({ x: countCandle.startFrame, y: dailyAve, startTs: countCandle.startFrame, endTs: countCandle.endFrame  })
        
        let countTotal = 0
        countChart.candles.slice(0, i + 1).forEach(c => countTotal += c.sum)
        let deathTotal = 0
        deathChart.candles.slice(0, i + 1).forEach(c => deathTotal += c.sum)
        const totalAve = deathTotal / countTotal
        totalData.push({ x: countCandle.startFrame, y: totalAve, startTs: countCandle.startFrame, endTs: countCandle.endFrame  })
    })
    
    return {
        total: totalData,
        daily: dailyData
    }
}

export const calcSpCount = (bukiPerformances: BukiPerformance[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    let spTotal = 0
    bukiPerformances.forEach(perf => {
        if (buki && perf.buki !== buki) {
            return
        }
        perf.events.forEach(evt => {
            if (rule && evt.rule !== rule) {
                return
            }
            if (stage && evt.stage !== stage) {
                return
            }
            spTotal += evt.spTrigger
        })
    })
    return spTotal
}

export const calcSpAve = (bukiPerformances: BukiPerformance[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon): number => {
    const spTotal = calcSpCount(bukiPerformances, rule, stage, buki)
    const count = calcBattleCount(bukiPerformances, rule, stage, buki)
    return count > 0 ? spTotal / count : 0
}

export const calcSpAveHistory = (stats: BattleStatistics[], rule?: BattleRule, stage?: BattleStage, buki?: MainWeapon, ignoreEnmtyPeriod: boolean=true): History => {
    const duration = 3600000 * 24
    const spChart = new CandleChart(duration, undefined, true, false)
    const countChart = new CandleChart(duration, undefined, true, false)
    
    stats.forEach(stat => {
        const battleDate = toZeroHour(stat.startTimestamp)
        const spTotal = calcSpCount(stat.bukiPerformances, rule, stage, buki)
        const battleCount = calcBattleCount(stat.bukiPerformances, rule, stage, buki)
        spChart.addValue({ value: spTotal, frame: battleDate }) 
        countChart.addValue({ value: battleCount, frame: battleDate }) 
    })

    const totalData: any[] = []
    const dailyData: any[] = []
    countChart.candles.forEach((countCandle, i) => {
        const spCandle = spChart.getCandle(i)!
        if (ignoreEnmtyPeriod && countCandle.isEmpty) {
            return
        }
        const dailyCount = countCandle.sum
        const dailyDeath = spCandle.sum
        const dailyAve = dailyDeath / dailyCount
        dailyData.push({ x: countCandle.startFrame, y: dailyAve, startTs: countCandle.startFrame, endTs: countCandle.endFrame  })
        
        let countTotal = 0
        countChart.candles.slice(0, i + 1).forEach(c => countTotal += c.sum)
        let deathTotal = 0
        spChart.candles.slice(0, i + 1).forEach(c => deathTotal += c.sum)
        const totalAve = deathTotal / countTotal
        totalData.push({ x: countCandle.startFrame, y: totalAve, startTs: countCandle.startFrame, endTs: countCandle.endFrame  })
    })
    
    return {
        total: totalData,
        daily: dailyData
    }
}