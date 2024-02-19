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
    
dirs = {
    '0': 'hiragana',
    '1': 'katakana',
    '2': 'number',
    '3': 'alphabet',
    '4': 'symbol',
    '5': 'greek',
    '6': 'rusian',
    '7': 'diacritical',
}

interval = 10
save_notif = False
save_count = True
src_dir = '/Users/maohika/Downloads/movies'
area_dir = '/Users/maohika/Downloads/battle_indicator'
dst_char_type_dir = '/Users/maohika/Downloads/char_type'
dst_char_dir = '/Users/maohika/Downloads/char'
model = YOLO("models/battle_indicator/best.pt")
char_model = YOLO("models/ocr/char_type/best.pt")
os.makedirs(area_dir, exist_ok=True)
os.makedirs(dst_char_type_dir, exist_ok=True) 

paths = list(Path(src_dir).rglob('*.mp4'))
paths.sort()
for path in paths:
    print(f'process: {path}')
    cap = cv2.VideoCapture(str(path))
    frame = 0
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
        out_img_name = f'{image_name}_{frame}'

        input = preprocess(img)
        preds = model.model(input, augment=False)
        preds = postprocess(preds,input,img)

        ind_box = []

        has_target = False
        for *xyxy, conf, cls in reversed(preds[0]):
            x1 = xyxy[0].numpy().astype('uint')
            y1 = xyxy[1].numpy().astype('uint')
            x2 = xyxy[2].numpy().astype('uint')
            y2 = xyxy[3].numpy().astype('uint')
            cls = cls.numpy().astype('uint')
            if cls <= 9:
                c_x = (x2 + x1) / 2
                c_y = (y2 + y1) / 2
                x = c_x / img.shape[1]
                y = c_y / img.shape[0]
                w = (x2 - x1) / img.shape[1]
                h = (y2 - y1) / img.shape[0]
                box = ' '.join([str(cls), str(x), str(y), str(w), str(h)])
                ind_box.append(box)
                if cls >= 3 and cls <= 8:
                    has_target = True

            if save_count and cls in [14, 15, 17, 18]:
                img_out = f'{dst_char_type_dir}/{out_img_name}.jpg'
                area_img = img[y1:y2, x1:x2]
                if area_img.size > 0:
                    cv2.imwrite(img_out, area_img)

                char_input = preprocess(area_img)
                char_preds = char_model.model(char_input, augment=False)
                char_preds = postprocess(char_preds,char_input,area_img)

                boxes = []
                char_idx = 0
                for *xyxy, conf, cls in reversed(char_preds[0]):
                    x1 = xyxy[0].numpy().astype('uint')
                    y1 = xyxy[1].numpy().astype('uint')
                    x2 = xyxy[2].numpy().astype('uint')
                    y2 = xyxy[3].numpy().astype('uint')
                    cls = cls.numpy().astype('uint')
                    c_x = (x2 + x1) / 2
                    c_y = (y2 + y1) / 2
                    x = c_x / area_img.shape[1]
                    y = c_y / area_img.shape[0]
                    w = (x2 - x1) / area_img.shape[1]
                    h = (y2 - y1) / area_img.shape[0]
                    box = ' '.join([str(cls), str(x), str(y), str(w), str(h)])
                    boxes.append(box)
                    char_img = area_img[y1:y2,x1:x2]
                    char_img_dir = f'{dst_char_dir}/{dirs[str(cls)]}'
                    os.makedirs(char_img_dir, exist_ok=True)
                    char_img_path = f'{char_img_dir}/{out_img_name}_{char_idx}.jpg'
                    if char_img.shape[0] >= 10 and char_img.shape[1] >= 10:
                        cv2.imwrite(char_img_path, char_img)
                        char_idx += 1
                boxes = sorted(boxes, key=lambda b: float(b.split(' ')[1]))
                txt_img_path = f'{dst_char_type_dir}/{out_img_name}.txt'
                f = open(txt_img_path, 'w')
                for b in boxes:
                    f.write(b + '\n')
                f.close()

        if len(ind_box) > 0 and has_target:
            ind_box = sorted(ind_box, key=lambda b: float(b.split(' ')[1]))
            txt_img_path = f'{area_dir}/{out_img_name}.txt'
            img_out_path =f'{area_dir}/{out_img_name}.jpg'
            cv2.imwrite(img_out_path, img)
            f = open(txt_img_path, 'w')
            for b in ind_box:
                f.write(b + '\n')
            f.close()

        frame += 1