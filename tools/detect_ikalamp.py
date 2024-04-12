import time
import shutil
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


buki_model = YOLO("models/buki/best.pt")
global idx
idx = 0
def detect_buki(pred, img, frame, dst_buki, image_name):
    global idx
    save_img = False
    buki_found = False
    for *xyxy, conf, cls in reversed(pred):
        if cls == 1 or cls == 4:
            continue
        save_img = True
        if conf >= 0.0:
            x1 = xyxy[0].numpy().astype('uint')
            y1 = xyxy[1].numpy().astype('uint')
            x2 = xyxy[2].numpy().astype('uint')
            y2 = xyxy[3].numpy().astype('uint')
            lamp = img[y1:y2, x1:x2]
            if lamp.size > 0:
                buki_res = buki_model.predict(lamp, verbose=False)[0]
                buki_name = buki_res.names[buki_res.probs.top1]
                out_path = f'{dst_buki}/' + buki_name
                if not os.path.exists(out_path):
                    os.makedirs(out_path)
                cv2.imwrite(f'{out_path}/{image_name}_{frame}.jpg', lamp)
                idx += 1
                buki_found = True

    #if save_img:
    if False:
        out_path = './temp/stage'
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        t = int(time.time() * 1000)
        cv2.imwrite(f'{out_path}/{t}.jpg', img)

    return buki_found

lamp_model = YOLO("models/ikalamp/best.pt")
ika_model = YOLO("models/ika/best.pt")

buki_detection = True
save_lamp = False
interval = 30
sp_death_th = 0
start_frame = 0 
src_dir = 'C:/work/movies/RECentral'
dst_buki = 'C:/work/temp/buki'
dst_lamp = 'C:/work/temp/ikalamp'
os.makedirs(dst_buki, exist_ok=True)
os.makedirs(dst_lamp, exist_ok=True)
paths = list(Path(src_dir).rglob('*.mp4'))
paths.sort()
for path in paths:
    print(f'process: {path}')
    cap = cv2.VideoCapture(str(path))
    frame = start_frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
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

        origin = deepcopy(img)
        lamp_annotator = Annotator(origin,line_width=1,example=str(lamp_model.model.names))
        ika_annotator = Annotator(origin,line_width=1,example=str(ika_model.model.names))
        img = preprocess(img)
        lamp_preds = lamp_model.model(img, augment=False)
        lamp_preds = postprocess(lamp_preds,img,origin)
        
        boxes = []
        has_timer = False
        live_count = 0
        death_count = 0
        sp_count = 0
        for *xyxy, conf, cls in reversed(lamp_preds[0]):
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
            if cls == 0:
                live_count += 1
            if cls == 1:
                death_count += 1
            if cls == 2:
                sp_count += 1
            if cls == 4:
                has_timer = True
        
        if save_lamp and len(boxes) == 9 and has_timer and (death_count + sp_count >= sp_death_th):
            boxes = sorted(boxes, key=lambda b: float(b.split(' ')[1]))
            txt_img_path = f'{dst_lamp}/{image_name}_{frame}.txt'
            img_out_path =f'{dst_lamp}/{image_name}_{frame}.jpg'
            cv2.imwrite(img_out_path, origin)
            f = open(txt_img_path, 'w')
            for b in boxes:
                f.write(b + '\n')
            f.close()
        
        if buki_detection:
            if detect_buki(lamp_preds[0], origin, frame, dst_buki, image_name):
                buki_frame_count += 1
        frame += 1