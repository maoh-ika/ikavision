from move_detection_files import move_files

label_list = [
#    'amabi',
#    'cyouzame',
#    'gonzui',
#    'hirame',
#    'kinmedai',
#    'konbu',
#    'kusaya',
#    'mahimahi',
#    'mantamaria',
#    'masaba',
#    'mategai',
#    'namerou',
#    'nampula',
#    'sumeshi',
#    'taraport',
#    'yagara',
#    'yunohana',
#    'zatou',
#    'takaashi',
#    'ohyou',
#    'bangaitei',
#    'negitoro',
    'kaziki'
]

src_dir = 'C:/work/temp/images'
dst_dir = '//wsl.localhost/Ubuntu-22.04/mnt/wsl/PHYSICALDRIVE1/splatoon3/dataset/stage/{label}'

for label in label_list:
    formated_src_dir = src_dir.format(label=label)
    formated_dst_dir = dst_dir.format(label=label)
    move_files(formated_src_dir, formated_dst_dir, label)