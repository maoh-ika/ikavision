from gen_train_dataset import gen_train_dataset

gen_train_dataset(
    src_dir='/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/sub_weapon/',
    train_dir='./dataset/sub_weapon/train/',
    val_dir='./dataset/sub_weapon/val/',
    train_ratio=0.8,
    shuffle=True
)
