import shutil
import os
from pathlib import Path
from ultralytics import YOLO
from ultralytics.data.augment import LetterBox
from ultralytics.utils.plotting import Annotator, colors
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
                                    agnostic=True,
                                    max_det=100)

    for i, pred in enumerate(preds):
        shape = orig_img.shape
        pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

    return preds

src_dir = './images/frames'
dst_dir = './images/position'
ika_model = YOLO("models/ika/best.pt")
os.makedirs(dst_dir, exist_ok=True)

paths = list(Path(src_dir).rglob('*.[jJ][pP][gG]'))
for name_idx, path in enumerate(paths):
    print(path)
    
    tokens = os.path.splitext(os.path.basename(path))
    image_name, image_ext = tokens[0], tokens[1]
    
    img = cv2.imread(str(path))

    pred = ika_model.track(img, persist=True, conf=0.3, iou=0.25, verbose=False)[0]
    for name_idx in range(len(pred.boxes.data)):
        x1 = int(pred.boxes.data[name_idx][0].cpu().numpy().astype('uint'))
        y1 = int(pred.boxes.data[name_idx][1].cpu().numpy().astype('uint'))
        x2 = int(pred.boxes.data[name_idx][2].cpu().numpy().astype('uint'))
        y2 = int(pred.boxes.data[name_idx][3].cpu().numpy().astype('uint'))
        conf = float(pred.boxes.conf[name_idx].cpu().numpy().astype('float'))
        cls = int(pred.boxes.cls[name_idx].cpu().numpy().astype('uint'))
        box = [x1, y1, x2, y2]
        track_id = int(pred.boxes.id[name_idx].cpu().numpy().astype('uint')) if pred.boxes.id is not None else None
        if cls == 0:
            name_img = img[y1:y2,x1:x2]
            name_img_path = f'{dst_dir}/{image_name}_{name_idx}{image_ext}'
            if name_img.size > 0:
                cv2.imwrite(name_img_path, name_img)
            