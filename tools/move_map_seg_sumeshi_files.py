from move_classification_files import move_files

label_list = [
    'seg_1',
    'seg_2',
    'seg_3',
    'seg_4',
    'seg_5',
    'seg_6',
    'seg_7',
    'seg_8',
    'seg_9',
    'seg_10',
    'seg_11',
    'seg_12',
    'seg_13',
    'seg_14',
    'seg_15',
    'seg_16',
    'seg_17',
    'seg_18',
    'seg_19',
    'seg_20',
]

src_dir = '/Users/maoh_ika/Documents/map_segment/sumeshi/{label}'
dst_dir = '/Volumes/GoogleDrive/My Drive/spla/dataset/map_segment/sumeshi/{label}'
move_files(label_list, src_dir, dst_dir, True)
