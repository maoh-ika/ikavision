import os
from gen_detection_dataset import get_dataset

src_dir='//wsl.localhost/Ubuntu-22.04/mnt/wsl/PHYSICALDRIVE1/splatoon3/dataset/stage/'
train_dir='./dataset/stage/train/'
val_dir='./dataset/stage/val/'
train_ratio=0.8

for label_dir in os.listdir(src_dir):
    print(f'exploring {label_dir}')
    get_dataset(f'{src_dir}/{label_dir}', train_dir, val_dir, train_ratio, shuffle=True, seed=11232329)