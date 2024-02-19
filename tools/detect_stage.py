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
                                    agnostic=True,
                                    max_det=100)

    for i, pred in enumerate(preds):
        shape = orig_img.shape
        pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

    return preds
    

src_dir = '/Users/maoh_ika/Downloads/stage/zatou'
dst_dir = '/Users/maoh_ika/Downloads/stage/zatou'
model = YOLO("models/stage/best.pt")
os.makedirs(dst_dir, exist_ok=True)

paths = list(Path(src_dir).rglob('*.[jJ][pP][gG]'))
paths.sort()
    
for idx, path in enumerate(paths):
    print(path)
    
    tokens = os.path.splitext(os.path.basename(path))
    image_name, image_ext = tokens[0], tokens[1]
    
    img = cv2.imread(str(path))
    input = preprocess(img)
    preds = model.model(input, augment=False)
    preds = postprocess(preds,input,img)

    boxes = []
    for *xyxy, conf, cls in reversed(preds[0]):
        x1 = xyxy[0].numpy().astype('uint')
        y1 = xyxy[1].numpy().astype('uint')
        x2 = xyxy[2].numpy().astype('uint')
        y2 = xyxy[3].numpy().astype('uint')
        cls = cls.numpy().astype('uint')
        c_x = (x2 + x1) / 2
        c_y = (y2 + y1) / 2
        x = c_x / img.shape[1]
        y = c_y / img.shape[0]
        w = (x2 - x1) / img.shape[1]
        h = (y2 - y1) / img.shape[0]
        box = ' '.join([str(cls), str(x), str(y), str(w), str(h)])
        boxes.append(box)
    
    if len(boxes) > 0:
        boxes = sorted(boxes, key=lambda b: float(b.split(' ')[1]))
        img_out_path =f'{dst_dir}/{image_name}.txt'
        f = open(img_out_path, 'w')
        for b in boxes:
            f.write(b + '\n')
        f.close()