import shutil
import os
from pathlib import Path
import cv2

src_dir = '/Users/maoh_ika/Downloads/ika'
dst_dir = '/Volumes/GoogleDrive/My Drive/spla/dataset/ika/orig'
name_pre = 'ika'

max_num = -1
for file_name in os.listdir(dst_dir):
    file_path = os.path.join(dst_dir, file_name)
    if os.path.isfile(file_path):
        try:
            tokens = os.path.splitext(os.path.basename(file_path))
            image_name, image_ext = tokens[0], tokens[1]
            i = int(image_name.split('_')[-1])
            if max_num < i:
                max_num = i
        except:
            pass

cur_idx = max_num + 1
    
for idx, path in enumerate(Path(src_dir).rglob('*.[jJ][pP][gG]')):
    print(path)
    
    tokens = os.path.splitext(os.path.basename(path))
    image_name, image_ext = tokens[0], tokens[1]
    out_img_name = f'{name_pre}_{cur_idx}'
    img_out = f'{dst_dir}/{out_img_name}{image_ext}'
    box_path = f'{src_dir}/{image_name}.txt'
    box_out = f'{dst_dir}/{out_img_name}.txt'

    if not os.path.exists(path) or not os.path.exists(box_path):
        continue
    
    if os.path.exists(img_out):
        raise Exception('already exists')
   
    shutil.copy(path, img_out)
    shutil.copy(box_path, box_out)
    cur_idx += 1

shutil.copy(src_dir + '/classes.txt', dst_dir + '/classes.txt')

