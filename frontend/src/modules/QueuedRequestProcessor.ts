import { PeriodicTask } from './PeriodicTask'

interface  QueueItem<ParamsType> {
  params: ParamsType
  success?: Function
  error?: Function
}

export abstract class QueuedRequestProcessor<ParamsType> extends PeriodicTask {
  interval: number
  items: QueueItem<ParamsType>[]
  concurrency: number 
  
  abstract _request(params: ParamsType): Promise<any>

  constructor(interval: number = 3000, concurrency: number = 1) {
    super()
    this.interval = interval
    this.concurrency = concurrency
    this.items = []
  }

  get size(): number {
    return this.items.length
  }

  start(): void {
    super.start(this._run.bind(this), this.interval)
  }

  add(request: ParamsType, success?: Function, error?: Function): void {
    this.items.push({
      params: request,
      success: success,
      error: error
    })
  }
  
  async _run(): Promise<void> {
    const promises: Promise<void>[] = []
    const items: any[] = []
    for (let i = 0; i < this.concurrency; ++i) {
      const item = this.items.shift()
      if (item === undefined) {
        continue
      }
      items.push(item)
      promises.push(this._request(item.params))
    }
    if (promises.length === 0) {
      return
    }
    try {
      const res = await Promise.all(promises)
      items.forEach((item, idx) => { if (item.success) item.success(res[idx]) })
    } catch (err) {
      items.forEach(item => { if (item.error) item.error(err) })
    }
  }
}