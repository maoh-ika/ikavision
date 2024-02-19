from gen_train_dataset import gen_train_dataset

char_types = [
    'all',
    'hiragana',
    'katakana',
    'symbol',
    'number',
    'alphabet',
    'greek',
    'rusian',
]

for ct in char_types:
    gen_train_dataset(
        src_dir=f'/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/ocr/{ct}/',
        train_dir=f'./dataset/ocr/{ct}/train/',
        val_dir=f'./dataset/ocr/{ct}/val/',
        train_ratio=0.8
    )
