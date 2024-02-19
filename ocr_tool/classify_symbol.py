import shutil
import os
from pathlib import Path
import cv2
from show_classification_dataset import count_labels

src_dir = '/Users/maohika/Downloads/char/symbol'
skip_dir = '/Users/maohika/Downloads/char/skipped'
dst_dir = '/Volumes/splatoon3/dataset/ocr/symbol'
os.makedirs(skip_dir, exist_ok=True)
target_label_count = 20000

def left_bracket():
    print(f'which left bracket type : 1: corner , 3: round, 5: large square 7: small square 9: curly')
    while True:
        key2 = cv2.waitKey(1)
        if key2 == ord('1'):
            return 'symbol_left_corner_bracket'
        elif key2 == ord('3'):
            return 'symbol_left_round_bracket'
        elif key2 == ord('5'):
            return 'symbol_left_square_bracket_large'
        elif key2 == ord('7'):
            return 'symbol_left_square_bracket_small'
        elif key2 == ord('9'):
            return 'symbol_left_curly_bracket'

def right_bracket():
    print(f'which right bracket type : 1: corner , 3: round, 5: large square 7: small square 9: curly')
    while True:
        key2 = cv2.waitKey(1)
        if key2 == ord('1'):
            return 'symbol_right_corner_bracket'
        elif key2 == ord('3'):
            return 'symbol_right_round_bracket'
        elif key2 == ord('5'):
            return 'symbol_right_square_bracket_large'
        elif key2 == ord('7'):
            return 'symbol_right_square_bracket_small'
        elif key2 == ord('9'):
            return 'symbol_right_curly_bracket'

def star():
    print(f'which star type : 1: stroke, 3: fill')
    while True:
        key2 = cv2.waitKey(1)
        if key2 == ord('1'):
            return 'symbol_star_stroke'
        elif key2 == ord('3'):
            return 'symbol_star_fill'

def diamond():
    print(f'which diamond type : 1: stroke, 3: fill')
    while True:
        key2 = cv2.waitKey(1)
        if key2 == ord('1'):
            return 'symbol_diamond_stroke'
        elif key2 == ord('3'):
            return 'symbol_diamond_fill'

def colon():
    print(f'which colon type : 1: semi, 3: colon')
    while True:
        key2 = cv2.waitKey(1)
        if key2 == ord('1'):
            return 'symbol_semicolon'
        elif key2 == ord('3'):
            return 'symbol_colon'

def asterisk():
    print(f'which asterisk type : 1: small, 3: large')
    while True:
        key2 = cv2.waitKey(1)
        if key2 == ord('1'):
            return 'symbol_asterisk_small'
        elif key2 == ord('3'):
            return 'symbol_asterisk_large'

def symbol():
    print(f'which symbol type')
    print(f'1: symbol_root')
    print(f'2: symbol_superset')
    print(f'3: symbol_equal')
    print(f'4: symbol_dollar')
    print(f'5: symbol_hat')
    print(f'6: symbol_greater_than')
    print(f'7: symbol_less_than')
    print(f'8: symbol_dagger')
    print(f'9: symbol_forall')
    print(f'q: symbol_because')
    print(f'w: symbol_yen')
    print(f'e: symbol_sime')
    print(f'r: symbol_question_mark')
    print(f't: symbol_plus_minus')
    while True:
        key2 = cv2.waitKey(1)
        if key2 == ord('1'):
            return 'symbol_root'
        elif key2 == ord('2'):
            return 'symbol_superset'
        elif key2 == ord('3'):
            return 'symbol_equal'
        elif key2 == ord('4'):
            return 'symbol_dollar'
        elif key2 == ord('5'):
            return 'symbol_hat'
        elif key2 == ord('6'):
            return 'symbol_greater_than'
        elif key2 == ord('7'):
            return 'symbol_less_than'
        elif key2 == ord('8'):
            return 'symbol_dagger'
        elif key2 == ord('9'):
            return 'symbol_forall'
        elif key2 == ord('q'):
            return 'symbol_because'
        elif key2 == ord('w'):
            return 'symbol_yen'
        elif key2 == ord('e'):
            return 'symbol_sime'
        elif key2 == ord('r'):
            return 'symbol_question_mark'
        elif key2 == ord('t'):
            return 'symbol_plus_minus'

symbol_map = {
    '6': 'symbol_amp',
    ';': 'symbol_plus',
    ':': asterisk,
    'd': 'symbol_diamond_stroke',
    '.': 'symbol_dot',
    '1': 'symbol_exclamation',
    '-': 'symbol_hyphen',
    'i': 'symbol_implies',
    '[': left_bracket,
    '5': 'symbol_percent',
    'r': 'symbol_registered_trademark',
    ']': right_bracket,
    'c': colon,
    '3': 'symbol_sharp',
    '7': 'symbol_single_dash',
    '/': 'symbol_slash',
    's': star,
    '^': 'symbol_tilde',
    'k': 'symbol_kuten',
    '9': 'symbol_backquote',
    'm': 'symbol_infinity',
    's': star,
    'o': 'symbol_eighth_note',
    '2': 'symbol_double_dash',
    'd': diamond,
    'z': symbol,
}

symbol_map = { ord(key): val for key, val in symbol_map.items() }

label_counts = count_labels(dst_dir)
sorted_label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
for label, count in sorted_label_counts:
    print(f"Label: {label}, Count: {count}")

for idx, path in enumerate(Path(src_dir).rglob('*.[jJ][pP][gG]')):
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
        if key in symbol_map:
            dir = symbol_map[key]
            if not isinstance(dir, str):
                dir = dir()
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
                print(f'reached label count target. delete.')
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
