import cv2
import os
from pathlib import Path

def save_all_frames(video_path, dir_path, basename, interval=10):
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
        if n % interval != 0:
            n += 1
            continue
        if not ret or frame is None:
            print(f'[{video_path}] failed to read frame')
            n += 1
            continue
        cv2.imwrite('{}_{}.{}'.format(base_path, str(image_count).zfill(digit), 'jpg'), frame)
        image_count += 1
        n += 1


src_dir = 'C:/work/temp/movies'
dst_dir = 'C:/work/temp/images'
os.makedirs(dst_dir, exist_ok=True)

paths = [src_dir]
paths = list(Path(src_dir).rglob('*.mp4'))
for path in paths:
    filename = os.path.basename(path)
    save_all_frames(str(path), dst_dir, filename, interval=30)
