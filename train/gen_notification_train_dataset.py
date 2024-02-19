from gen_detection_dataset import get_dataset

src_dir = '/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/notification'
train_dir = './dataset/notification/train/'
val_dir = './dataset/notification/val/'
train_ratio = 0.8

get_dataset(
    src_dir=src_dir,
    train_dir=train_dir,
    val_dir=val_dir,
    train_ratio=train_ratio,
    shuffle=True
)
