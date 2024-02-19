import type { AnalysisResultSammary } from '@/modules/AnalysisResultApi'

export class BattleTimer {
    readonly result: AnalysisResultSammary
    readonly movieSeconds: number
    readonly battleSeconds: number
    readonly battleOpenSecond: number
    readonly battleEndSecond: number
    readonly resultStartSecond: number
    readonly resultEndSecond: number

    constructor(result: AnalysisResultSammary) {
        this.result = result
        this.movieSeconds = result.movieFrames / result.frameRate
        this.battleSeconds = this.convertFrameToBattleSecond(result.battleEndFrame) - this.convertFrameToBattleSecond(result.battleOpenFrame)
        this.battleOpenSecond = this.convertFrameToMovieSecond(result.battleOpenFrame)
        this.battleEndSecond = this.convertFrameToMovieSecond(result.battleEndFrame)
        this.resultStartSecond = this.convertFrameToMovieSecond(result.resultStartFrame)
        this.resultEndSecond = this.convertFrameToMovieSecond(result.resultEndFrame)
    }

    convertMovieSecondToBattleSecond(movieTime: number): number {
        return movieTime - this.battleOpenSecond
    }

    convertBattleSecondToMovieSecond(battleTime: number): number {
        return battleTime + this.battleOpenSecond
    }

    convertFrameToMovieSecond(frame: number): number {
        return frame / this.result.frameRate
    }

    convertFrameToBattleSecond(frame: number): number {
        return (frame - this.result.battleOpenFrame) / this.result.frameRate
    }

    convertMovieTimeToMovieFrame(time: number): number {
        return Math.floor(this.result.movieFrames * (time / this.movieSeconds))
    }
}