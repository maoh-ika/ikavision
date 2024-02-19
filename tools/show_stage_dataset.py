import os
from pathlib import Path

dataset_dir = f'/Users/maohika/Library/CloudStorage/GoogleDrive-maohika@ikaruga_app/My Drive/spla/dataset/stage/orig/'
label_counts = {}

for stage_dir in os.listdir(dataset_dir):
    if stage_dir in ['0_shortcut', '.DS_Store']:
        continue
    if stage_dir not in label_counts:
        label_counts[stage_dir] = 0
    for path in Path(dataset_dir + stage_dir).rglob('*.[jJpP][pPnN][gG]'):
        if path.parent.name == 'temp':
            continue
        label_counts[stage_dir] += 1

sorted_label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

for label, count in sorted_label_counts:
    print(f"Label: {label}, Count: {count}")