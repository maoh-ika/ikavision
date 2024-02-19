from gen_detection_dataset import get_dataset

src_dir = '/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/plate'
train_dir = './dataset/plate/train/'
val_dir = './dataset/plate/val/'
train_ratio = 0.8

get_dataset(src_dir, train_dir, val_dir, train_ratio, shuffle=True, seed=11152127)
