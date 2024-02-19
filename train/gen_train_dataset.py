import os
from pathlib import Path
import cv2
import shutil
import random

def gen_train_dataset(
    src_dir,
    train_dir,
    val_dir,
    train_ratio,
    shuffle=False,
    seed=None,
    max_data_count=None
):
    for buki_dir in os.listdir(src_dir):
        print(f'exploring {buki_dir}')
        paths = [str(path) for path in Path(src_dir + buki_dir).rglob('*.[jJpP][pPnN][gG]') if path.parent.name != 'temp']
        if shuffle:
            random.seed(seed)
            random.shuffle(paths)
        else:
            paths.sort()
        
        if max_data_count and max_data_count > 0:
            paths = paths[:max_data_count]

        train_count = int(len(paths) * train_ratio)
        val_count = len(paths) - train_count

        if train_count <= 0 or val_count <= 0:
            print(f'not enough dataset: {buki_dir}')
            continue
        
        train_out_dir = train_dir + buki_dir
        if not os.path.exists(train_out_dir):
            os.makedirs(train_out_dir)

        for i in range(train_count):
            path = paths[i]
            image_name = os.path.basename(path)
    #        img = cv2.imread(path)
    #        img = cv2.resize(img, img_size)
    #        cv2.imwrite('/'.join([train_out_dir, image_name]), img)
            out_path = '/'.join([train_out_dir, image_name])
            if not os.path.exists(out_path):
                if cv2.imread(path) is None:
                    raise Exception(f'  unavailable {path}')
                print(f'copy train: {path}')
                shutil.copy(path, out_path)

        val_out_dir = val_dir + buki_dir
        if not os.path.exists(val_out_dir):
            os.makedirs(val_out_dir)
        
        for i in range(val_count):
            path = paths[i + train_count]
            image_name = os.path.basename(path)
    #        img = cv2.imread(path)
    #        img = cv2.resize(img, img_size)
    #        cv2.imwrite('/'.join([val_out_dir, image_name]), img)
            out_path = '/'.join([val_out_dir, image_name])
            if not os.path.exists(out_path):
                if cv2.imread(path) is None:
                    print(f'  unavailable {path}')
                    continue
                print(f'copy val: {path}')
                shutil.copy(path, out_path)