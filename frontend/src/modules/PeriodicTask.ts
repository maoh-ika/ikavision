export class PeriodicTask {
  timerId?: number
  once: boolean

  constructor(once: boolean = false) {
    this.once = once
  }

  get isRunning(): boolean {
    return this.timerId !== undefined
  }

  start(func: Function, interval: number, args?: any): void {
    if (this.isRunning) {
      return
    }
    setTimeout(func, 0, args)
    if (this.once) {
      return
    }

    const task = () => {
      const a = Date.now()
      try {
        func(args)
      } catch (err) {
        console.log(err)
      }
      const procTime = Date.now() - a
      const sleepTime = procTime < interval ? interval - procTime : 0
      this.timerId = window.setTimeout(task, sleepTime)
    }
    this.timerId = window.setTimeout(task, interval)
  }

  stop(): void {
    if (this.isRunning) {
      window.clearInterval(this.timerId)
      this.timerId = undefined
    }
  }
}