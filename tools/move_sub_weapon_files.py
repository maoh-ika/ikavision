from move_classification_files import move_files

kana_list = [
    #'splash_bomb',
    #'kyuuban_bomb',
    #'quick_bomb',
    'sprinkler',
    #'splash_shield',
    #'tansan_bomb',
    #'curling_bomb',
    #'robot_bomb',
    #'jump_beacon',
    #'point_sensor',
    #'trap',
    #'poison_mist',
    #'line_marker',
    #'torpede'
]

src_dir = '/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/sub_weapon/{label}/temp'
dst_dir = '/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/sub_weapon/{label}'
move_files(kana_list, src_dir, dst_dir, copy=True)