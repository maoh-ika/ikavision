import time
from ultralytics import YOLO
import torch
import cv2
import os
import random
from pathlib import Path
from ultralytics.data.augment import LetterBox
from ultralytics.utils.plotting import Annotator, colors
from ultralytics.utils import ops
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt

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
                                    0.25,
                                    0.8,
                                    agnostic=True,
                                    max_det=100)

    for i, pred in enumerate(preds):
        shape = orig_img.shape
        pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

    return preds

def drow_bbox(pred, names, annotator):
    for *xyxy, conf, cls in reversed(pred):
        c = int(cls)  # integer class
        label =  f'{names[c]} {conf:.2f}'
        annotator.box_label(xyxy, label, color=colors(c, True), )


ika_model = YOLO("models/ika/best.pt")

src_dir = '/Users/maoh_ika/Downloads/temp/weapons'
dst_dir = '/Users/maoh_ika/Downloads/ika'
paths = list(Path(src_dir).rglob('*.mp4'))
paths.sort()
for path in paths:
    tokens = os.path.splitext(os.path.basename(path))
    file_name, ext = tokens[0], tokens[1]
    
    print(f'process: {path}')
    cap = cv2.VideoCapture(str(path))
    frame = 0
    buki_frame_count = 0
    while True:
        ret, img = cap.read()
        if not ret:
            break

        if frame % 10 != 0:
            frame += 1
            continue

        origin = deepcopy(img)
        img = preprocess(img)
        ika_preds = ika_model.model(img, augment=False)
        ika_preds = postprocess(ika_preds,img,origin)
        boxes = []
        char_idx = 0
        for *xyxy, conf, cls in reversed(ika_preds[0]):
            x1 = xyxy[0].numpy().astype('uint')
            y1 = xyxy[1].numpy().astype('uint')
            x2 = xyxy[2].numpy().astype('uint')
            y2 = xyxy[3].numpy().astype('uint')
            cls = cls.numpy().astype('uint')
            c_x = (x2 + x1) / 2
            c_y = (y2 + y1) / 2
            x = c_x / origin.shape[1]
            y = c_y / origin.shape[0]
            w = (x2 - x1) / origin.shape[1]
            h = (y2 - y1) / origin.shape[0]
            box = ' '.join([str(cls), str(x), str(y), str(w), str(h)])
            boxes.append(box)

        if len(boxes) == 0:
            frame += 1
            continue
        
        img_out = f'{dst_dir}/{file_name}_{frame}.jpg'
        cv2.imwrite(img_out, origin)
        
        boxes = sorted(boxes, key=lambda b: float(b.split(' ')[1]))
        cls_out = f'{dst_dir}/{file_name}_{frame}.txt'
        f = open(cls_out, 'w')
        for b in boxes:
            f.write(b + '\n')
        f.close()
        
        frame += 1