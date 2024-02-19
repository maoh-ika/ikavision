export interface InvocationLog {
  owner: string
  creator: string
  timestamp: number
}

export interface LogPeriod {
  start: number
  end: number
  logs: InvocationLog[]
}
