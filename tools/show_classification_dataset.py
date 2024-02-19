import os
from pathlib import Path

# トレーニングデータセットのディレクトリ
dataset_dir = '/Volumes/splatoon3/dataset/stage/orig'

# ラベルごとのデータ数を格納する辞書

def count_labels(dataset_dir):
    if not dataset_dir.endswith('/'):
        dataset_dir += '/'
    label_counts = {}
    for buki_dir in os.listdir(dataset_dir):
        if buki_dir in ['0_shortcut', '.DS_Store']:
            continue
        paths = list(Path(dataset_dir + buki_dir).rglob('*.[jJpP][pPnN][gG]'))
        label_counts[buki_dir] = len(paths)
    return label_counts

if __name__ == '__main__':
    label_counts = count_labels(dataset_dir)
    sorted_label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

    for label, count in sorted_label_counts:
        print(f"Label: {label}, Count: {count}")