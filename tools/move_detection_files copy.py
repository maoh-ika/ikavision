import shutil
import os
from pathlib import Path
import cv2



src_dir = '/Users/maoh_ika/Downloads/weapon_gauge'
dst_dir = '/Users/maoh_ika/Downloads/weapon_gauge'
txt = '/Users/maoh_ika/Downloads/weapon_gauge/96deco.mp4_0000.txt'

cls = open(txt).read()

for idx, path in enumerate(Path(src_dir).rglob('*.[jJ][pP][gG]')):
    print(path)
    
    tokens = os.path.splitext(os.path.basename(path))
    image_name, image_ext = tokens[0], tokens[1]
    box_path = f'{src_dir}/{image_name}.txt'

    if os.path.exists(box_path):
        continue

    shutil.copy(txt, box_path)
