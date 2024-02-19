import shutil
import os
from pathlib import Path
import cv2
from show_classification_dataset import count_labels

src_dir = '/Users/maohika/Downloads/char/alphabet'
skip_dir = '/Users/maohika/Downloads/char/skipped'
dst_dir = '/Users/maohika/Downloads/char_data/alphabet'
os.makedirs(skip_dir, exist_ok=True)
os.makedirs(dst_dir, exist_ok=True)
target_label_count = 10000

lower_map = {
    'a': 'alphabet_a',
    'b': 'alphabet_b',
    'c': 'alphabet_c',
    'd': 'alphabet_d',
    'e': 'alphabet_e',
    'f': 'alphabet_f',
    'g': 'alphabet_g',
    'h': 'alphabet_h',
    'i': 'alphabet_i',
    'j': 'alphabet_j',
    'k': 'alphabet_k',
    'l': 'alphabet_l',
    'm': 'alphabet_m',
    'n': 'alphabet_n',
    'o': 'alphabet_o',
    'p': 'alphabet_p',
    'q': 'alphabet_q',
    'r': 'alphabet_r',
    's': 'alphabet_s',
    't': 'alphabet_t',
    'u': 'alphabet_u',
    'v': 'alphabet_v',
    'w': 'alphabet_w',
    'x': 'alphabet_x',
    'y': 'alphabet_y',
    'z': 'alphabet_z'
}

upper_map = {
    'a': 'alphabet_a_upper',
    'b': 'alphabet_b_upper',
    'c': 'alphabet_c_upper',
    'd': 'alphabet_d_upper',
    'e': 'alphabet_e_upper',
    'f': 'alphabet_f_upper',
    'g': 'alphabet_g_upper',
    'h': 'alphabet_h_upper',
    'i': 'alphabet_i_upper',
    'j': 'alphabet_j_upper',
    'k': 'alphabet_k_upper',
    'l': 'alphabet_l_upper',
    'm': 'alphabet_m_upper',
    'n': 'alphabet_n_upper',
    'o': 'alphabet_o_upper',
    'p': 'alphabet_p_upper',
    'q': 'alphabet_q_upper',
    'r': 'alphabet_r_upper',
    's': 'alphabet_s_upper',
    't': 'alphabet_t_upper',
    'u': 'alphabet_u_upper',
    'v': 'alphabet_v_upper',
    'w': 'alphabet_w_upper',
    'x': 'alphabet_x_upper',
    'y': 'alphabet_y_upper',
    'z': 'alphabet_z_upper'
}

lower_map = { ord(key): val for key, val in lower_map.items() }
upper_map = { ord(key): val for key, val in upper_map.items() }

label_counts = count_labels(dst_dir)
sorted_label_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

for label, count in sorted_label_counts:
    print(f"Label: {label}, Count: {count}")

for idx, path in enumerate(Path(src_dir).rglob('*.[jJ][pP][gG]')):
    print(path)
    tokens = os.path.splitext(os.path.basename(path))
    image_name, image_ext = tokens[0], tokens[1]

    img = cv2.imread(str(path))
    if img.shape[0] < 10 or img.shape[1] < 10:
        print('small image. delete.')
        os.remove(path)
        continue

    ratio = img.shape[0] / img.shape[1]
    img = cv2.resize(img, (100, int(100 * ratio)))
    cv2.imshow(image_name, img)
    
    dir = None
    while dir is None:
        key = cv2.waitKey(1)
        if key in lower_map:
            print(f'use upper case for {image_name}? : y: upper, n: lower')
            while True:
                key2 = cv2.waitKey(1)
                if key2 == ord('y'):
                    dir = upper_map[key]
                    break
                elif key2 == ord('n'):
                    dir = lower_map[key]
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
