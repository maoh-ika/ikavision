import os
from gen_detection_dataset import get_dataset

src_dir='/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/stage'
train_dir='./dataset/stage/train/'
val_dir='./dataset/stage/val/'
train_ratio=0.8

for label_dir in os.listdir(src_dir):
    print(f'exploring {label_dir}')
    get_dataset(f'{src_dir}/{label_dir}', train_dir, val_dir, train_ratio, shuffle=True, seed=11232329)