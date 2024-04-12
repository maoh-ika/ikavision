export type MainWeapon =
  'unknown' |
  'bold_marker' |
  'bold_marker_neo' |
  'wakaba_shooter' |
  'momiji_shooter' |
  'promodeler_mg' |
  'promodeler_rg' |
  'sharp_marker' |
  'sharp_marker_neo' |
  'spla_shooter' |
  'hero_shooter_replica' |
  'spla_shooter_collabo' |
  'nzap85' |
  'nzap89' |
  '52gallon' |
  'prime_shooter' |
  'prime_shooter_collabo' |
  '96gallon' |
  '96gallon_deco' |
  'jet_sweeper' |
  'jet_sweeper_custom' |
  'space_shooter' |
  'space_shooter_collabo' |
  'l3_reelgun' |
  'l3_reelgun_d' |
  'h3_reelgun' |
  'h3_reelgun_d' |
  'bottole_kaiser' |
  'carbon_roller' |
  'carbon_roller_deco' |
  'spla_roller' |
  'spla_roller_collabo' |
  'dynamo_roller' |
  'dynamo_roller_tesla' |
  'variable_roller' |
  'wide_roller' |
  'wide_roller_collabo' |
  'classic_squiffer' |
  'spla_charger' |
  'spla_scope' |
  'spla_charger_collabo' |
  'spla_scope_collabo' |
  'eliter_4k' |
  '4k_scope' |
  '14shiki_takedutsu_kou' |
  'soy_tuber' |
  'soy_tuber_custom' |
  'rpen_5h' |
  'nova_blaster' |
  'nova_blaster_neo' |
  'hot_blaster' |
  'long_blaster' |
  'rapid_blaster' |
  'rapid_blaster_deco' |
  'r_blaster_elite' |
  'r_blaster_elite_deco' |
  'crash_blaster' |
  'crash_blaster_neo' |
  'sblast92' |
  'hissen' |
  'hissen_nouveau' |
  'bucket_slosher' |
  'bucket_slosher_deco' |
  'screw_slosher' |
  'screw_slosher_neo' |
  'over_flosher' |
  'over_flosher_deco' |
  'explosher' |
  'spla_spiner' |
  'spla_spiner_collabo' |
  'barrel_spiner' |
  'barrel_spiner_deco' |
  'hydrant' |
  'kugelschreiber' |
  'kugelschreiber_nouveau' |
  'nautilus47' |
  'pablo' |
  'pablo_nouveau' |
  'hokusai' |
  'hokusai_nouveau' |
  'vincent' |
  'dapple_dualies' |
  'dapple_dualies_nouveau' |
  'spla_maneuver' |
  'dual_sweeper' |
  'dual_sweeper_custom' |
  'kelvin535' |
  'quad_hopper_black' |
  'quad_hopper_white' |
  'para_shelter' |
  'para_shelter_solare' |
  'camping_shelter' |
  'camping_shelter_solare' |
  'spy_gadget' |
  'tri_stringer' |
  'tri_stringer_collabo' |
  'lact450' |
  'drive_wiper' |
  'drive_wiper_deco' |
  'gym_wiper' |
  'examiner' |
  'moplin' |
  'bottole_kaiser_foil' |
  'gym_wiper_nouveau' |
  'hot_blaster_custom' |
  'lact450_deco' |
  'rpen_5b' |
  'sblast91' |
  'spla_maneuver_collabo' |
  'spy_gadget_solare' |
  'vincent_nouveau' |
  'octa_shooter_replica' |
  'order_blaster_replica' |
  'order_brush_replica' |
  'order_charger_replica' |
  'order_maneuver_replica' |
  'order_roller_replica' |
  'order_shelter_replica' |
  'order_shooter_replica' |
  'order_spinner_replica' |
  'order_stringer_replica' |
  'order_wiper_replica' |
  'classic_squiffer_beta' |
  '24shiki_harikaegasa_kou' |
  '52gallon_deco' |
  'moplin_d' |
  'eliter_4k_custom' |
  'gaen_ff' |
  'variable_roller_foil' |
  '4k_scope_custom' |
  'nautilus79' |
  'explosher_custom' |
  'kelvin525_deco'

export type SubWeapon =
  'unknown' |
  'splash_bomb' |
  'kyuuban_bomb' |
  'quick_bomb' |
  'sprinkler' |
  'splash_shield' |
  'tansan_bomb' |
  'curling_bomb' |
  'robot_bomb' |
  'jump_beacon' |
  'point_sensor' |
  'trap' |
  'poison_mist' |
  'line_marker' |
  'torpede'

export type SpecialWeapon =
  'unknown' |
  'kani_tank' |
  'syoku_wonder' |
  'kyuuinki' |
  'energy_stand' |
  'hop_sonar' |
  'same_ride' |
  'decoy_tirashi' |
  'great_barrier' |
  'ultra_shoot' |
  'megaphone_laser_51ch' |
  'triple_tornade' |
  'teioh_ika' |
  'multi_missile' |
  'jet_pack' |
  'amefurashi' |
  'ultra_hanko' |
  'nice_dama' |
  'ultra_tyakuti' |
  'suminaga_sheet'

export interface MainWeaponSpec {
  bukiId: MainWeapon
  subWeapon: SubWeapon,
  specialWeapon: SpecialWeapon
}

export interface SubWeaponSpec {
  bukiId: SubWeapon
  inkConsumptionPercent: number
}

export interface SpecialWeaponSpec {
  bukiId: SpecialWeapon
}

export interface Buki {
  mainWeapon: MainWeapon
  subWeapon: SubWeapon
  specialWeapon: SpecialWeapon
  subInkConsumption: number
}

export const allMains: MainWeapon[] = [
  'bold_marker',
  'bold_marker_neo',
  'wakaba_shooter',
  'momiji_shooter',
  'promodeler_mg',
  'promodeler_rg',
  'sharp_marker',
  'sharp_marker_neo',
  'spla_shooter',
  'hero_shooter_replica',
  'spla_shooter_collabo',
  'nzap85',
  'nzap89',
  '52gallon',
  'prime_shooter',
  'prime_shooter_collabo',
  '96gallon',
  '96gallon_deco',
  'jet_sweeper',
  'jet_sweeper_custom',
  'space_shooter',
  'space_shooter_collabo',
  'l3_reelgun',
  'l3_reelgun_d',
  'h3_reelgun',
  'h3_reelgun_d',
  'bottole_kaiser',
  'carbon_roller',
  'carbon_roller_deco',
  'spla_roller',
  'spla_roller_collabo',
  'dynamo_roller',
  'dynamo_roller_tesla',
  'variable_roller',
  'wide_roller',
  'wide_roller_collabo',
  'classic_squiffer',
  'spla_charger',
  'spla_scope',
  'spla_charger_collabo',
  'spla_scope_collabo',
  'eliter_4k',
  '4k_scope',
  '14shiki_takedutsu_kou',
  'soy_tuber',
  'soy_tuber_custom',
  'rpen_5h',
  'nova_blaster',
  'nova_blaster_neo',
  'hot_blaster',
  'long_blaster',
  'rapid_blaster',
  'rapid_blaster_deco',
  'r_blaster_elite',
  'r_blaster_elite_deco',
  'crash_blaster',
  'crash_blaster_neo',
  'sblast92',
  'hissen',
  'hissen_nouveau',
  'bucket_slosher',
  'bucket_slosher_deco',
  'screw_slosher',
  'screw_slosher_neo',
  'over_flosher',
  'over_flosher_deco',
  'explosher',
  'spla_spiner',
  'spla_spiner_collabo',
  'barrel_spiner',
  'barrel_spiner_deco',
  'hydrant',
  'kugelschreiber',
  'kugelschreiber_nouveau',
  'nautilus47',
  'pablo',
  'pablo_nouveau',
  'hokusai',
  'hokusai_nouveau',
  'vincent',
  'dapple_dualies',
  'dapple_dualies_nouveau',
  'spla_maneuver',
  'dual_sweeper',
  'dual_sweeper_custom',
  'kelvin535',
  'quad_hopper_black',
  'quad_hopper_white',
  'para_shelter',
  'para_shelter_solare',
  'camping_shelter',
  'camping_shelter_solare',
  'spy_gadget',
  'tri_stringer',
  'tri_stringer_collabo',
  'lact450',
  'drive_wiper',
  'drive_wiper_deco',
  'gym_wiper',
  'examiner',
  'moplin',
  'bottole_kaiser_foil',
  'gym_wiper_nouveau',
  'hot_blaster_custom',
  'lact450_deco',
  'rpen_5b',
  'sblast91',
  'spla_maneuver_collabo',
  'spy_gadget_solare',
  'vincent_nouveau'
]

export const allSubs: SubWeapon[] = [
  'splash_bomb',
  'kyuuban_bomb',
  'quick_bomb',
  'sprinkler',
  'splash_shield',
  'tansan_bomb',
  'curling_bomb',
  'robot_bomb',
  'jump_beacon',
  'point_sensor',
  'trap',
  'poison_mist',
  'line_marker',
  'torpede'
]

export const allSpecials: SpecialWeapon[] = [
  'kani_tank',
  'syoku_wonder',
  'kyuuinki',
  'energy_stand',
  'hop_sonar',
  'same_ride',
  'decoy_tirashi',
  'great_barrier',
  'ultra_shoot',
  'megaphone_laser_51ch',
  'triple_tornade',
  'teioh_ika',
  'multi_missile',
  'jet_pack',
  'amefurashi',
  'ultra_hanko',
  'nice_dama',
  'ultra_tyakuti',
  'suminaga_sheet'
]