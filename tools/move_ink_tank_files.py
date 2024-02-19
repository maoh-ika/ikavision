import shutil
import os
from pathlib import Path
import requests
import cv2
import json

src_dir = './images/position'
dst_dir = '/Users/maohika/Library/CloudStorage/GoogleDrive-maohika@ikaruga_app/My Drive/spla/dataset/ink_tank'
name_pre = 'ink_tank'

max_num = -1
for file_name in os.listdir(dst_dir):
    file_path = os.path.join(dst_dir, file_name)
    if os.path.isfile(file_path):
        try:
            tokens = os.path.splitext(os.path.basename(file_path))
            image_name, image_ext = tokens[0], tokens[1]
            i = int(image_name.split('_')[-1])
            if max_num < i:
                max_num = i
        except:
            pass

cur_idx = max_num + 1
    
for idx, path in enumerate(Path(src_dir).rglob('*.[jJ][pP][gG]')):
    print(path)
    
    img_full_name = os.path.basename(path)
    tokens = os.path.splitext(img_full_name)
    image_name, image_ext = tokens[0], tokens[1]
    out_img_name = f'{name_pre}_{cur_idx}'
    img_out = f'{dst_dir}/{out_img_name}{image_ext}'

    seg_data = json.loads(requests.get(f"http://localhost/api/json/%2F{img_full_name}").text)
    if 'objects' not in seg_data:
        continue
    
    image = cv2.imread(str(path))
    height = image.shape[0]
    width = image.shape[1]

    seg_txt = ''
    for object in seg_data['objects']:
        seg_txt += str(object['classIndex'])
        for point in object['polygon']:
          seg_txt += ' '
          seg_txt += str(point['x'] / width)
          seg_txt += ' '
          seg_txt += str(point['y'] / height)
        seg_txt += '\n'

    box_out = f'{dst_dir}/{out_img_name}.txt'

    if os.path.exists(img_out):
        raise Exception('already exists')
   
    shutil.copy(path, img_out)
    with open(box_out, 'w') as f:
        f.write(seg_txt)
    cur_idx += 1
