
export type BattleSide =
    'team' |
    'enemy'

export type BattleWinLose =
    'win' |
    'lose' |
    'draw'

export type IkalampState =
    'live' |
    'death' |
    'sp' |
    'drop'

export type BattleRule =
    'nawabari' |
    'area' |
    'yagura' |
    'hoko' |
    'asari' |
    'unknown'

export type BattleStage = 
    'amabi' |
    'cyouzame' |
    'gonzui' |
    'hirame' |
    'kinmedai' |
    'konbu' |
    'kusaya' |
    'mahimahi' |
    'mantamaria' |
    'masaba' |
    'mategai' |
    'namerou' |
    'nampula' |
    'sumeshi' |
    'taraport' |
    'yagara' |
    'yunohana' |
    'zatou' |
    'takaashi' |
    'ohyou' |
    'bangaitei' |
    'negitoro' |
    'map' |
    'unknown'

export type MatchType = 
    'unknown' |
    'regular_match' |
    'bankara_match' |
    'x_match' |
    'event_match' |
    'fes_match' |
    'priv_match'

export type XMatchRate =
  'under_1500' |
  '1500_2000' |
  '2000_2500' |
  '2500_3000' |
  '3000_3500' |
  '3500_4000' |
  'upper_4000'

export type DeathReasonType = 
    'main_weapon' |
    'sub_weapon' |
    'sp_weapon' |
    'hoko_shoot' |
    'other' |
    'unknown'

export interface Ikalamp {
  side: BattleSide
  state: IkalampState
  bukiId: string
  xywh: number[]
  ord: number
  playImageWidth: number
  playImageHeight: number
  timestamp: number
  lowAccuracy: boolean
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

export const allRules: BattleRule[] = [
    'nawabari',
    'area',
    'yagura',
    'hoko',
    'asari'
]

export const allStages: BattleStage[] = [
    'amabi',
    'cyouzame',
    'gonzui',
    'hirame',
    'kinmedai',
    'konbu',
    'kusaya',
    'mahimahi',
    'mantamaria',
    'masaba',
    'mategai',
    'namerou',
    'nampula',
    'sumeshi',
    'taraport',
    'yagara',
    'yunohana',
    'zatou',
    'takaashi',
    'ohyou',
    'bangaitei',
    'negitoro'
]

export const allMatchTypes: MatchType[] = [
    'regular_match',
    'bankara_match',
    'x_match',
    'event_match',
    'fes_match',
    'priv_match'
]

export const allXMatchRates: XMatchRate[] = [
  'under_1500',
  '1500_2000',
  '2000_2500',
  '2500_3000',
  '3000_3500',
  '3500_4000',
  'upper_4000'
]