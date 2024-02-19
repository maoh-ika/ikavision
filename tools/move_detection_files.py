import shutil
import os
from pathlib import Path
import cv2

def find_next_idx(dst_dir):
    max_num = -1
    paths = [str(path) for path in Path(dst_dir).rglob('*.txt') if path.parent.name != "temp"]
    for file_path in paths:
        try:
            tokens = os.path.splitext(os.path.basename(file_path))
            image_name, image_ext = tokens[0], tokens[1]
            if image_name == 'classes.txt':
                pass
            i = int(image_name.split('_')[-1])
            if max_num < i:
                max_num = i
        except:
            pass

    return max_num + 1

def move_files(src_dir, dst_dir, prefix):
    os.makedirs(dst_dir, exist_ok=True)

    cur_idx = find_next_idx(dst_dir)

    paths = list(Path(src_dir).rglob('*.[jJ][pP][gG]'))
    paths.sort()
    for idx, path in enumerate(paths):
        print(path)
        
        tokens = os.path.splitext(os.path.basename(path))
        image_name, image_ext = tokens[0], tokens[1]
        out_img_name = f'{prefix}_{cur_idx}'
        img_out = f'{dst_dir}/{out_img_name}{image_ext}'
        box_path = f'{src_dir}/{image_name}.txt'
        box_out = f'{dst_dir}/{out_img_name}.txt'

        if not os.path.exists(path) or not os.path.exists(box_path):
            continue

        with open(box_path) as f:
            if f.read() == '':
                continue
        
        if os.path.exists(img_out):
            raise Exception('already exists')
    
        print(f'copy {path} to {img_out}')
        shutil.copy(path, img_out)
        shutil.copy(box_path, box_out)
        cur_idx += 1

    #shutil.copy(src_dir + '/classes.txt', dst_dir + '/classes.txt')

