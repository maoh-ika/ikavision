import shutil
import os
from pathlib import Path
import cv2
from show_classification_dataset import count_labels

src_dir = '/Users/maohika/Downloads/char/symbol'
skip_dir = '/Users/maohika/Downloads/char/skipped'
dst_dir = '/Volumes/splatoon3/dataset/ocr/number'
os.makedirs(skip_dir, exist_ok=True)
target_label_count = 10000

number_map = {
    '1': 'number_1',
    '2': 'number_2',
    '3': 'number_3',
    '4': 'number_4',
    '5': 'number_5',
    '6': 'number_6',
    '7': 'number_7',
    '8': 'number_8',
    '9': 'number_9',
    '0': 'number_0',
    '.': 'decimal_point',
}

number_map = { ord(key): val for key, val in number_map.items() }

label_counts = count_labels(dst_dir)
sorted_label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
for label, count in sorted_label_counts:
    print(f"Label: {label}, Count: {count}")

paths = list(Path(src_dir).rglob('*.[jJ][pP][gG]'))
paths.sort()
for idx, path in enumerate(paths):
    print(path)
    tokens = os.path.splitext(os.path.basename(path))
    image_name, image_ext = tokens[0], tokens[1]

    img = cv2.imread(str(path))
    ratio = img.shape[0] / img.shape[1]
    img = cv2.resize(img, (100, int(100 * ratio)))
    cv2.imshow(image_name, img)
    
    dir = None
    while dir is None:
        key = cv2.waitKey(1)
        if key in number_map:
            dir = number_map[key]
        elif key == ord(' '):
            print('skip')
            img_out = f'{skip_dir}/{image_name}{image_ext}'
            shutil.move(path, img_out)
            break
        elif key == 127:
            print('delete')
            cv2.destroyWindow(image_name)
            os.remove(path)
            break

    if dir:
        if label_counts[dir] >= target_label_count:
            print('reached label count target. delete.')
            os.remove(path)
            continue
        label_counts[dir] += 1
        print(f'save to {dir}')
        print(f'total count {dir}: {label_counts[dir]}')
        out_dir = f'{dst_dir}/{dir}/temp'
        os.makedirs(out_dir, exist_ok=True)
        img_out = f'{out_dir}/{image_name}{image_ext}'
        if os.path.exists(img_out):
            print('already exists. delete.')
            os.remove(path)
        else:
            shutil.move(path, img_out)

    cv2.destroyWindow(image_name)
