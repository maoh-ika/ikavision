import os
from pathlib import Path

data_path = '/media/maohika/1c0ddf00-ee1d-46f9-b3bb-e958e891243f/splatoon3/dataset/match'

label_counts = {}
classes = {}
with open(f'{data_path}/classes.txt') as f:
    for i, cls in enumerate(f.readlines()):
        classes[i] = cls.replace('\n', '')
        label_counts[i] = 0

for idx, path in enumerate(Path(data_path).rglob('*.txt')):
    name = os.path.basename(path)
    if name == 'classes.txt':
        continue
    with open(path) as f:
        for line in f.readlines():
            tokens = line.split(' ')
            if len(tokens) > 0:
                cls = int(tokens[0])
                if cls not in label_counts:
                    label_counts[cls] = 1
                else:
                    label_counts[cls] += 1


label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

for label, count in label_counts:
    print(f"Label: {classes[label]}, Count: {count}")