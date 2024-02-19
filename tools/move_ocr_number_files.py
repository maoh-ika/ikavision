from move_classification_files import move_files

alp_list = [
    'number_1',
    'number_2',
    'number_3',
    'number_4',
    'number_5',
    'number_6',
    'number_7',
    'number_8',
    'number_9',
    'number_0',
    'decimal_point'
]

src_dir = '/Users/maohika/Downloads/char/number/{label}'
dst_dir = '/Volumes/splatoon3/dataset/ocr/number/{label}'
move_files(alp_list, src_dir, dst_dir)