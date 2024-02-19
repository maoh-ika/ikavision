export interface CandleValue {
    value: number
    frame: number
}

export class Candle {
    startFrame: number
    endFrame: number
    values: CandleValue[]

    constructor(startFrame: number, endFrame: number) {
        this.startFrame = startFrame
        this.endFrame = endFrame
        this.values = []
    }

    addValue(value: CandleValue): boolean {
        if (value.frame < this.startFrame || this.endFrame <= value.frame) {
            return false
        }
        this.values.push(value)
        return true
    }

    get isEmpty(): boolean {
        return this.values.length === 0
    }

    get openValue(): CandleValue | undefined {
        return this.isEmpty ? undefined : this.values[0]
    }

    get closeValue(): CandleValue | undefined {
        return this.isEmpty ? undefined : this.values[this.values.length - 1]
    }

    get average(): number {
        return this.isEmpty ? 0 : this.sum / this.values.length
    }

    get sum(): number {
        let sum = 0
        this.values.forEach(v => sum += v.value)
        return sum
    }
}

export class CandleChart {
    maxCandleCount: number
    candleDuration: number
    fillWithBlank: boolean
    isFixedPeriod: boolean
    candles: Candle[]

    constructor(candleDuration: number, maxCandleCount: number=0, fillWithBlank:boolean=true, isFixedPeriod: boolean=true) {
        this.maxCandleCount = maxCandleCount
        this.candleDuration = candleDuration
        this.fillWithBlank = fillWithBlank
        this.isFixedPeriod = isFixedPeriod
        this.candles = []
    }

    get firstCandle(): Candle | undefined {
        return this.isEmpty ? undefined : this.candles[0]
    }
    
    get lastCandle(): Candle | undefined {
        return this.isEmpty ? undefined : this.candles[this.candles.length - 1]
    }

    get isEmpty(): boolean {
        return this.candles.length === 0
    }

    getCandle(index: number): Candle | undefined {
        return index < this.candles.length ? this.candles[index] : undefined
    }
   
    addValue(value: CandleValue): Candle | undefined {
        if (this.isEmpty) {
            const candle = this.makeCandle(value)
            this.candles.push(candle)
            return candle
        }

        let newCandle = undefined
        if (value.frame < this.firstCandle!.startFrame) {
            newCandle = this.makeCandle(value)
            if (this.fillWithBlank) {
                const blankTicks = Math.floor((Math.abs(newCandle.endFrame - this.firstCandle!.startFrame)) / this.candleDuration)
                for (let _ = 0; _ <  blankTicks; ++_) {
                    const blank = this.makeBlankCandleBackward(this.candles[0])
                    this.candles.unshift(blank)
                }
            }
            this.candles.unshift(newCandle)
        } else if (this.lastCandle!.endFrame <= value.frame) {
            // add new candle and fill blank periods
            newCandle = this.makeCandle(value)
            if (this.fillWithBlank) {
                const blankTicks = Math.floor((newCandle.startFrame - this.lastCandle!.endFrame) / this.candleDuration)
                for (let _ = 0; _ <  blankTicks; ++_) {
                    const blank = this.makeBlankCandleForward(this.candles[this.candles.length - 1])
                    this.candles.push(blank)
                }
            }
            this.candles.push(newCandle)
        } else {
            // update current candle
            for (const candle of [...this.candles].reverse()) {
                if (candle.addValue(value)) {
                    break
                }
            }
        }
        
        if (this.maxCandleCount > 0) {
            while (this.maxCandleCount < this.candles.length) {
                this.candles.shift()
            }
        }
        
        return newCandle
    }

    makeCandle(value: CandleValue): Candle {
        const period = this.calCandlePeriod(value.frame)
        const candle = new Candle(period[0], period[1])
        candle.addValue(value)
        return candle
    }
    
    makeBlankCandleBackward(nextCandle: Candle): Candle {
        const nextEnd = nextCandle.startFrame
        const nextStart = nextEnd - this.candleDuration
        const candle = new Candle(nextStart, nextEnd)
        return candle
    }

    makeBlankCandleForward(prevCandle: Candle): Candle {
        const nextStart = prevCandle.endFrame
        const nextEnd = nextStart + this.candleDuration
        const candle = new Candle(nextStart, nextEnd)
        return candle
    }

    calCandlePeriod(frame: number): number[] {
        const mod = this.isFixedPeriod ? frame % this.candleDuration : 0
        const startFrame = frame - mod
        const endFrame = startFrame + this.candleDuration
        return [startFrame, endFrame]
    }
}