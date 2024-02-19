import shutil
import os
from pathlib import Path
from ultralytics import YOLO
from ultralytics.data.augment import LetterBox
from ultralytics.utils import ops
import numpy as np
import cv2
import torch

def preprocess(img, size=640):
        img = LetterBox(size, True)(image=img)
        img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        img = np.ascontiguousarray(img)  # contiguous
        img = torch.from_numpy(img)
        img = img.float()  # uint8 to fp16/32
        img /= 255  # 0 - 255 to 0.0 - 1.0
        return img.unsqueeze(0)

def postprocess(preds, img, orig_img):
    preds = ops.non_max_suppression(preds,
                                    agnostic=False,
                                    max_det=100)

    for i, pred in enumerate(preds):
        shape = orig_img.shape
        pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

    return preds
    

interval = 10
src_dir = '/Users/maohika/Downloads/movies'
dst_dir = '/Users/maohika/Downloads/weapon_gauge'
model = YOLO("models/weapon_gauge/best.pt")
os.makedirs(f'{dst_dir}/gauge', exist_ok=True)
os.makedirs(f'{dst_dir}/sub', exist_ok=True)
os.makedirs(f'{dst_dir}/sp', exist_ok=True)

paths = list(Path(src_dir).rglob('*.mp4'))
paths.sort()

for path in paths:
    print(f'process: {path}')
    cap = cv2.VideoCapture(str(path))
    frame = 0
#    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
    buki_frame_count = 0
    while True:
        ret, img = cap.read()
        if not ret:
            break
        if frame % interval != 0:
            frame += 1
            continue
    
        tokens = os.path.splitext(os.path.basename(path))
        image_name, image_ext = tokens[0], tokens[1]
        image_name = f'{image_name}_{frame}'
        
        input = preprocess(img)
        preds = model.model(input, augment=False)
        preds = postprocess(preds,input,img)

        for *xyxy, conf, cls in reversed(preds[0]):
            x1 = xyxy[0].numpy().astype('uint')
            y1 = xyxy[1].numpy().astype('uint')
            x2 = xyxy[2].numpy().astype('uint')
            y2 = xyxy[3].numpy().astype('uint')
            gauge_img = img[y1:y2, x1:x2]
            if cls == 0:
                img_out = f'{dst_dir}/gauge/{image_name}_gauge.jpg'
                cv2.imwrite(img_out, gauge_img)
            elif cls == 1:
                img_out = f'{dst_dir}/sub/{image_name}_sub.jpg'
                cv2.imwrite(img_out, gauge_img)
            elif cls == 2:
                img_out = f'{dst_dir}/sp/{image_name}_sp.jpg'
                cv2.imwrite(img_out, gauge_img)
        
        frame += 1
