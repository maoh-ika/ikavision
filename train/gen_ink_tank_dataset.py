from gen_detection_dataset import get_dataset

src_dir = '/home/maohika/gdrive/spla/dataset/ink_tank'
train_dir = './dataset/ink_tank/train/'
val_dir = './dataset/ink_tank/val/'
train_ratio = 0.8

get_dataset(
    src_dir=src_dir,
    train_dir=train_dir,
    val_dir=val_dir,
    train_ratio=train_ratio
)