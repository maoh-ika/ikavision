from move_classification_files import move_files

alp_list = [
    'rusian_ya',
]

src_dir = '/Users/maohika/Downloads/char/rusian/{label}'
dst_dir = '/Volumes/splatoon3/dataset/ocr/rusian/{label}'
move_files(alp_list, src_dir, dst_dir)