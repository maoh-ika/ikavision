
import shutil
import os
import threading
from pathlib import Path
import cv2

def move_files(label_list, src_dir, dst_dir, copy=False, postfix=None, remove_dot_only=False):
    threads = []
    for label in label_list:
        th = threading.Thread(target=_move, args=(label, src_dir, dst_dir, copy, postfix, remove_dot_only))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

def _move(label, src_dir, dst_dir, copy, postfix, remove_dot_only):
    print(f'moving: {label}')

    formated_src_dir = src_dir.format(label=label)
    formated_dst_dir = dst_dir.format(label=label)
    name_pre = label if postfix is None else f'{label}_{postfix}'
    
    paths = list(Path(formated_src_dir).rglob('*.[jJ][pP][gG]'))
    if len(paths) == 0 and not remove_dot_only:
        print(f'{label} no image found')
        return

    os.makedirs(formated_dst_dir, exist_ok=True)
    
    max_num = -1
    for file_name in os.listdir(formated_dst_dir):
        file_path = os.path.join(formated_dst_dir, file_name)
        if os.path.isfile(file_path):
            try:
                tokens = os.path.splitext(os.path.basename(file_path))
                image_name, image_ext = tokens[0], tokens[1]
                if image_name.startswith('.'):
                    continue
                i = int(image_name.split('_')[-1])
                if max_num < i:
                    max_num = i
            except:
                pass


    idx_offset = max_num + 1
    paths.sort()

    print(f'next idx: {idx_offset}')

    idx = 0 
    for _, path in enumerate(paths):
        tokens = os.path.splitext(os.path.basename(path))
        image_name, image_ext = tokens[0], tokens[1]
        if image_name.startswith('.'):
            print('remove dot file')
            os.remove(path)
            continue

        if remove_dot_only:
            continue

        img = cv2.imread(str(path))
        if img.shape[0] < 10 or img.shape[1] < 10:
            print('small image. delete.')
            os.remove(path)
            continue

        out_img_name = f'{name_pre}_{idx + idx_offset}'
        img_out = f'{formated_dst_dir}/{out_img_name}{image_ext}'

        if os.path.exists(img_out):
            raise Exception('already exists')
        if copy:
            print(f'copy {path} to {img_out}')
            shutil.copy(path, img_out)
        else:
            print(f'move {path} to {img_out}')
            ret = shutil.move(path, img_out)

        idx += 1

    # remove dot files
    paths = list(Path(formated_dst_dir).rglob('*.[jJ][pP][gG]'))
    for _, path in enumerate(paths):
        tokens = os.path.splitext(os.path.basename(path))
        image_name, image_ext = tokens[0], tokens[1]
        if image_name.startswith('.'):
            print('remove dot file')
            os.remove(path)
            continue