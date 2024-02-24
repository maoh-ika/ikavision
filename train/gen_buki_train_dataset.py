from gen_train_dataset import gen_train_dataset

gen_train_dataset(
    src_dir='//wsl.localhost/Ubuntu-22.04/mnt/wsl/PHYSICALDRIVE1/splatoon3/dataset/buki/orig/',
    train_dir='./dataset/buki/train/',
    val_dir='./dataset/buki/val/',
    train_ratio=0.8,
    shuffle=True,
    seed=10241940,
    max_data_count=1000
)
