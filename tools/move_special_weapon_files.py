from move_classification_files import move_files

kana_list = [
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

src_dir = '/Users/maohika/Downloads/weapons_sp/{label}'
dst_dir = '/Volumes/splatoon3/dataset/special_weapon/{label}'
move_files(kana_list, src_dir, dst_dir, copy=True)
