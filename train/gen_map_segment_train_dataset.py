from pathlib import Path
import os
import cv2

src_dir = '/home/maohika/gdrive/spla/dataset/map_segment/sumeshi/'
train_dir = './dataset/map_segment/sumeshi/train/'
val_dir = './dataset/map_segment/sumeshi/val/'
train_ratio = 0.8
    
for label in os.listdir(src_dir):
    print(f'generate from {label}')
    paths = [str(path) for path in Path(src_dir + label).rglob('*.mp4')]
    paths.sort()

    for path in paths[:2]:
        cap = cv2.VideoCapture(path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        train_count = int(total_frames * train_ratio)
        val_count = total_frames - train_count
        mov_name = os.path.basename(path)

        train_out_dir = train_dir + label
        os.makedirs(train_out_dir, exist_ok=True)

        for i in range(train_count):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, img = cap.read()
            if not ret:
                break
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            out_path = '/'.join([train_out_dir, f'{label}_{mov_name}_{i}.jpg'])
            cv2.imwrite(out_path, img)

        val_out_dir = val_dir + label
        os.makedirs(val_out_dir, exist_ok=True)
        
        for i in range(val_count):
            frame = train_count + i
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, img = cap.read()
            if not ret:
                break
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            out_path = '/'.join([val_out_dir, f'{label}_{mov_name}_{frame}.jpg'])
            cv2.imwrite(out_path, img)
        