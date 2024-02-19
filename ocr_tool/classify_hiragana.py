import shutil
import os
import random
from pathlib import Path
import cv2
from show_classification_dataset import count_labels

src_dir = '/Users/maoh_ika/Downloads/char/hiragana'
skip_dir = '/Users/maoh_ika/Downloads/char/skipped'
dst_dir = '/Volumes/splatoon3/dataset/ocr/hiragana'
os.makedirs(skip_dir, exist_ok=True)
target_label_count = 20000

hiragana_map = {
    '3': 'hiragana_a',
    'e': 'hiragana_i',
    '4': 'hiragana_u',
    '5': 'hiragana_e',
    '6': 'hiragana_o',
    't': 'hiragana_ka',
    'g': 'hiragana_ki',
    'h': 'hiragana_ku',
    ':': 'hiragana_ke',
    'b': 'hiragana_ko',
    'x': 'hiragana_sa',
    'd': 'hiragana_si',
    'r': 'hiragana_su',
    'p': 'hiragana_se',
    'c': 'hiragana_so',
    'q': 'hiragana_ta',
    'a': 'hiragana_ti',
    'z': 'hiragana_tu',
    'w': 'hiragana_te',
    's': 'hiragana_to',
    'u': 'hiragana_na',
    'i': 'hiragana_ni',
    '1': 'hiragana_nu',
    ',': 'hiragana_ne',
    'k': 'hiragana_no',
    'f': 'hiragana_ha',
    'v': 'hiragana_hi',
    '2': 'hiragana_hu',
    '^': 'hiragana_he',
    '-': 'hiragana_ho',
    'j': 'hiragana_ma',
    'n': 'hiragana_mi',
    ']': 'hiragana_mu',
    '/': 'hiragana_me',
    'm': 'hiragana_mo',
    '7': 'hiragana_ya',
    '8': 'hiragana_yu',
    '9': 'hiragana_yo',
    'o': 'hiragana_ra',
    'l': 'hiragana_ri',
    '.': 'hiragana_ru',
    ';': 'hiragana_re',
    '_': 'hiragana_ro',
    '0': 'hiragana_wa',
    '¥': 'hiragana_wo',
    'y': 'hiragana_n',
}

dakuten_map = {
    't': 'hiragana_ga',
    'g': 'hiragana_gi',
    'h': 'hiragana_gu',
    ':': 'hiragana_ge',
    'b': 'hiragana_go',
    'x': 'hiragana_za',
    'd': 'hiragana_zi',
    'r': 'hiragana_zu',
    'p': 'hiragana_ze',
    'c': 'hiragana_zo',
    'q': 'hiragana_da',
    'a': 'hiragana_di',
    'z': 'hiragana_du',
    'w': 'hiragana_de',
    's': 'hiragana_do',
    'f': 'hiragana_ba',
    'v': 'hiragana_bi',
    '2': 'hiragana_bu',
    '^': 'hiragana_be',
    '-': 'hiragana_bo',
}
handakuten_map = {
    'f': 'hiragana_pa',
    'v': 'hiragana_pi',
    '2': 'hiragana_pu',
    '^': 'hiragana_pe',
    '-': 'hiragana_po',
}

hiragana_map = { ord(key): val for key, val in hiragana_map.items() }
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

    if img.shape[0] < 10 or img.shape[1] < 10:
        print('small image. delete.')
        os.remove(path)
        continue
    
    img = cv2.resize(img, (100, 100))
    ratio = img.shape[0] / img.shape[1]
    img = cv2.resize(img, (100, int(100 * ratio)))
    cv2.imshow(image_name, img)
    
    dir = None
    while dir is None:
        key = cv2.waitKey(1)
        if key in hiragana_map:
            has_dakuten = key in dakuten_map
            has_handakuten = key in handakuten_map
            if not has_dakuten and not has_handakuten:
                dir = hiragana_map[key]
                break
            elif has_dakuten and not has_handakuten:
                print(f'use dakuten for {image_name}?, y: dakuten, n: hiragana')
                while True:
                    key2 = cv2.waitKey(1)
                    if key2 == ord('y'):
                        dir = dakuten_map[key]
                        break
                    elif key2 == ord('n'):
                        dir = hiragana_map[key]
                        break
            elif not has_dakuten and has_handakuten:
                raise Exception('invalid char')
            elif has_dakuten and has_handakuten:
                print(f'use dakuten for {image_name}? : d: dakuten, h: handakuten, n: hiragana')
                while True:
                    key2 = cv2.waitKey(1)
                    if key2 == ord('d'):
                        dir = dakuten_map[key]
                        break
                    elif key2 == ord('h'):
                        dir = handakuten_map[key]
                        break
                    elif key2 == ord('n'):
                        dir = hiragana_map[key]
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
        if dir not in label_counts:
            label_counts[dir] = 1
        else:
            if label_counts[dir] >= target_label_count:
                print(f'{dir} is reached label count target. delete.')
                os.remove(path)
                cv2.destroyWindow(image_name)
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
