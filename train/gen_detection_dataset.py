import shutil
import os
from pathlib import Path
import cv2
import random

src_dir = '/Users/maohika/Library/CloudStorage/GoogleDrive-maohika@ikaruga_app/My Drive/spla/dataset/ika/orig/'
train_dir = './dataset/ika/train/'
val_dir = './dataset/ika/val/'
train_ratio = 0.8

def _copy(path, dst_dir):
    image_name = os.path.basename(path)

    img_dir = os.path.dirname(path) 
    tokens = os.path.splitext(os.path.basename(path))
    image_name, image_ext = tokens[0], tokens[1]
    img_out = f'{dst_dir}/{image_name}{image_ext}'
    if cv2.imread(path) is None:
        raise Exception(f'  unavailable {path}')
    shutil.copy(path, img_out)

    box_path = f'{img_dir}/{image_name}.txt'
    box_out = f'{dst_dir}/{image_name}.txt'
    shutil.copy(box_path, box_out)

def get_dataset(src_dir, train_dir, val_dir, train_ratio, shuffle=False, seed=None):
    paths = [str(path) for path in Path(src_dir).rglob('*.[jJpP][pPnN][gG]')]
    paths.sort()
    if shuffle:
        random.seed(seed)
        random.shuffle(paths)
    train_count = int(len(paths) * train_ratio)
    val_count = len(paths) - train_count

    train_out_dir = train_dir 
    if not os.path.exists(train_out_dir):
        os.makedirs(train_out_dir)

    for i in range(train_count):
        _copy(paths[i], train_out_dir)


    val_out_dir = val_dir 
    if not os.path.exists(val_out_dir):
        os.makedirs(val_out_dir)

    for i in range(val_count):
        _copy(paths[i + train_count], val_out_dir)