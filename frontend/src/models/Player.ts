import type { BattleSide } from '@/models/Battle'

export enum IkaPlayerState {
  live,
  death,
  drop
}

export interface IkaPlayer {
  id?: string
  name: string
  nickname?: string
  side: BattleSide
  lamp_ord: number
}