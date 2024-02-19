export type ViewComponent = 
    'BattleMoviePlayer' |
    'InkTankLevelChart' |
    'PlayerNumberBalanceChart' |
    'BattleScoreChart' |
    'DeathChart' |
    'SpecialWeaponChart'

export interface ComponentConfig {
    component: ViewComponent
}

export interface SizeConfig {
    threshold: number
    width: number
    height: number
}

export interface BattleViewerConfig {
    size: SizeConfig[]
    components: ComponentConfig[]
    movieSyncEnabled: boolean
    playOnlyBattlePart: boolean
}