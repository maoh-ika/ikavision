from gen_detection_dataset import get_dataset

src_dir = '/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/weapon_gauge'
train_dir = './dataset/weapon_gauge/train/'
val_dir = './dataset/weapon_gauge/val/'
train_ratio = 0.8

get_dataset(
    src_dir=src_dir,
    train_dir=train_dir,
    val_dir=val_dir,
    train_ratio=train_ratio,
    shuffle=True
)