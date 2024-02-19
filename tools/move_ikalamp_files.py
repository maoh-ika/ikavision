import cv2
from move_detection_files import move_files

src_dir = '/Users/maoh_ika/Downloads/ikalamp_data'
dst_dir = '/Volumes/splatoon3/dataset/ikalamp'
name_pre = 'ikalamp'

move_files(src_dir, dst_dir, name_pre)