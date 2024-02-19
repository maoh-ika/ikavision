import shutil
import os
import random
from pathlib import Path
import cv2
from show_classification_dataset import count_labels

src_dir = '/Users/maoh_ika/Downloads/char/katakana'
skip_dir = '/Users/maoh_ika/Downloads/char/skipped'
dst_dir = '/Volumes/splatoon3/dataset/ocr/katakana'
os.makedirs(skip_dir, exist_ok=True)
target_label_count = 20000

katakana_map = {
    '3': 'katakana_a',
    'e': 'katakana_i',
    '4': 'katakana_u',
    '5': 'katakana_e',
    '6': 'katakana_o',
    't': 'katakana_ka',
    'g': 'katakana_ki',
    'h': 'katakana_ku',
    ':': 'katakana_ke',
    'b': 'katakana_ko',
    'x': 'katakana_sa',
    'd': 'katakana_si',
    'r': 'katakana_su',
    'p': 'katakana_se',
    'c': 'katakana_so',
    'q': 'katakana_ta',
    'a': 'katakana_ti',
    'z': 'katakana_tu',
    'w': 'katakana_te',
    's': 'katakana_to',
    'u': 'katakana_na',
    'i': 'katakana_ni',
    '1': 'katakana_nu',
    ',': 'katakana_ne',
    'k': 'katakana_no',
    'f': 'katakana_ha',
    'v': 'katakana_hi',
    '2': 'katakana_hu',
    '^': 'katakana_he',
    '-': 'katakana_ho',
    'j': 'katakana_ma',
    'n': 'katakana_mi',
    ']': 'katakana_mu',
    '/': 'katakana_me',
    'm': 'katakana_mo',
    '7': 'katakana_ya',
    '8': 'katakana_yu',
    '9': 'katakana_yo',
    'o': 'katakana_ra',
    'l': 'katakana_ri',
    '.': 'katakana_ru',
    ';': 'katakana_re',
    '_': 'katakana_ro',
    '0': 'katakana_wa',
    '¥': 'katakana_wo',
    'y': 'katakana_n',
}

dakuten_map = {
    '4': 'katakana_vu',
    't': 'katakana_ga',
    'g': 'katakana_gi',
    'h': 'katakana_gu',
    ':': 'katakana_ge',
    'b': 'katakana_go',
    'x': 'katakana_za',
    'd': 'katakana_zi',
    'r': 'katakana_zu',
    'p': 'katakana_ze',
    'c': 'katakana_zo',
    'q': 'katakana_da',
    'a': 'katakana_di',
    'z': 'katakana_du',
    'w': 'katakana_de',
    's': 'katakana_do',
    'f': 'katakana_ba',
    'v': 'katakana_bi',
    '2': 'katakana_bu',
    '^': 'katakana_be',
    '-': 'katakana_bo',
}
handakuten_map = {
    'f': 'katakana_pa',
    'v': 'katakana_pi',
    '2': 'katakana_pu',
    '^': 'katakana_pe',
    '-': 'katakana_po',
}

katakana_map = { ord(key): val for key, val in katakana_map.items() }
dakuten_map = { ord(key): val for key, val in dakuten_map.items() }
handakuten_map = { ord(key): val for key, val in handakuten_map.items() }

label_counts = count_labels(dst_dir)
sorted_label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
for label, count in sorted_label_counts:
    print(f"Label: {label}, Count: {count}")

paths = list(Path(src_dir).rglob('*.[jJ][pP][gG]'))
random.shuffle(paths)
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
        if key in katakana_map:
            has_dakuten = key in dakuten_map
            has_handakuten = key in handakuten_map
            if not has_dakuten and not has_handakuten:
                dir = katakana_map[key]
                break
            elif has_dakuten and not has_handakuten:
                print(f'use dakuten for {image_name}?, y: dakuten, n: katakana')
                while True:
                    key2 = cv2.waitKey(1)
                    if key2 == ord('y'):
                        dir = dakuten_map[key]
                        break
                    elif key2 == ord('n'):
                        dir = katakana_map[key]
                        break
            elif not has_dakuten and has_handakuten:
                raise Exception('invalid char')
            elif has_dakuten and has_handakuten:
                print(f'use dakuten for {image_name}? : d: dakuten, h: handakuten, n: katakana')
                while True:
                    key2 = cv2.waitKey(1)
                    if key2 == ord('d'):
                        dir = dakuten_map[key]
                        break
                    elif key2 == ord('h'):
                        dir = handakuten_map[key]
                        break
                    elif key2 == ord('n'):
                        dir = katakana_map[key]
                        break
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
            print('reached label count target. delete')
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
