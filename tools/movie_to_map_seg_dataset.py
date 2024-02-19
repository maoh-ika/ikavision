import cv2
import os
from pathlib import Path

def save_all_frames(video_path, dir_path, basename, ext='jpg'):
    cap = cv2.VideoCapture(video_path)
    print(f'process {video_path}')

    if not cap.isOpened():
        print(f'[{video_path}] failed to open file')
        return

    os.makedirs(dir_path, exist_ok=True)
    base_path = os.path.join(dir_path, basename)

    fps = round(cap.get(cv2.CAP_PROP_FPS))
    fps = 1
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    digit = len(str(frame_count))

    n = 0
    image_count = 0

    while n < frame_count:
        ret, frame = cap.read()
        if n % fps != 0:
            n += 1
            continue
        if not ret or frame is None:
            print(f'[{video_path}] failed to read frame')
            n += 1
            continue
        cv2.imwrite('{}_{}.{}'.format(base_path, str(image_count).zfill(digit), ext), frame)
        image_count += 1
        n += 1

src_dir = '/Users/maoh_ika/Library/Mobile Documents/com~apple~CloudDocs/Documents/dataset/movie'
dst_base = '/Users/maoh_ika/Library/Mobile Documents/com~apple~CloudDocs/Documents/dataset/map_segment'

paths = list(Path(src_dir).rglob('*.mp4'))
for path in paths:
    filename = os.path.basename(path)
    tokens = filename.split('_')
    stage = tokens[0]
    seg_num = tokens[2]
    dst_dir = f'{dst_base}/{stage}/seg_{seg_num}'
    save_all_frames(str(path), dst_dir, filename)
