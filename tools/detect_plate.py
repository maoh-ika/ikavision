import shutil
import os
from pathlib import Path
from ultralytics import YOLO
from ultralytics.data.augment import LetterBox
from ultralytics.utils import ops
from battle_analyzer.prediction.cls_to_char import hiragana_map, katakana_map, number_map, alphabet_map, symbol_map, greek_map, rusian_map, diacritical_map
import numpy as np
import cv2
import torch

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
    
def make_plate(model, plate_img):
    input = preprocess(plate_img, model.overrides['imgsz'])
    preds = model.model(input)
    pred = postprocess(preds, input, plate_img)[0]
    player_id = None
    player_name = None
    nickname = None
    boxes = []
    for *xyxy, conf, cls in pred:
        x1 = int(xyxy[0].cpu().numpy().astype('uint'))
        y1 = int(xyxy[1].cpu().numpy().astype('uint'))
        x2 = int(xyxy[2].cpu().numpy().astype('uint'))
        y2 = int(xyxy[3].cpu().numpy().astype('uint'))
        conf = float(conf.cpu().numpy().astype('float'))
        cls = int(cls.cpu().numpy().astype('uint'))
        c_x = (x2 + x1) / 2
        c_y = (y2 + y1) / 2
        x = c_x / notif_img.shape[1]
        y = c_y / notif_img.shape[0]
        w = (x2 - x1) / notif_img.shape[1]
        h = (y2 - y1) / notif_img.shape[0]
        box = ' '.join([str(cls), str(x), str(y), str(w), str(h)])
        boxes.append(box)
        content_img = plate_img[y1:y2,x1:x2]
        if cls == 0:
            player_name = content_img
        elif cls == 1:
            player_id = content_img
        elif cls == 2:
            nickname = content_img

    return player_name, player_id, nickname, boxes

def classify(char_img, model):
    char_res = model.predict(char_img, verbose=False)[0]
    return char_res.names[char_res.probs.top1]

def char_dir(cls):
    if cls in hiragana_map:
        return 'hiragana'
    elif cls in katakana_map:
        return 'katakana'
    elif cls in alphabet_map:
        return 'alphabet'
    elif cls in number_map:
        return 'number'
    elif cls in symbol_map:
        return 'symbol'
    elif cls in greek_map:
        return 'greek'
    elif cls in rusian_map:
        return 'rusian'
    elif cls in diacritical_map:
        return 'diacritical'
    else:
        return None

def detect_chars(notif_img, out_path, char_image_name):
    os.makedirs(dst_char_dir, exist_ok=True)
    char_input = preprocess(notif_img)
    char_preds = chartype_model.model(char_input, augment=False)
    char_preds = postprocess(char_preds,char_input,notif_img)
    boxes = []
    pred = char_preds[0]
    pred = sorted(pred, key=lambda b: b[0])
    char_idx = 0
    for *xyxy, conf, cls in pred:
        x1 = xyxy[0].numpy().astype('uint')
        y1 = xyxy[1].numpy().astype('uint')
        x2 = xyxy[2].numpy().astype('uint')
        y2 = xyxy[3].numpy().astype('uint')
        cls = cls.numpy().astype('uint')
        c_x = (x2 + x1) / 2
        c_y = (y2 + y1) / 2
        x = c_x / notif_img.shape[1]
        y = c_y / notif_img.shape[0]
        w = (x2 - x1) / notif_img.shape[1]
        h = (y2 - y1) / notif_img.shape[0]
        box = ' '.join([str(cls), str(x), str(y), str(w), str(h)])
        boxes.append(box)
        
        char_img = notif_img[y1:y2,x1:x2]
        char_cls = classify(char_img, all_model)
        char_img_dir = f'{dst_char_dir}/{char_dir(char_cls)}'
        char_img_dir = f'{char_img_dir}/{char_cls}'

        os.makedirs(char_img_dir, exist_ok=True)
        char_img_path = f'{char_img_dir}/{char_image_name}_{char_idx}.jpg'
        if char_img.shape[0] >= 10 and char_img.shape[1] >= 10:
            cv2.imwrite(char_img_path, char_img)
            char_idx += 1
    f = open(out_path, 'w')
    for b in boxes:
        f.write(b + '\n')
    f.close()

interval = 30
save_plate = False
save_kill = False
save_fullcharge = False
save_notif = True
src_dir = '/Users/maoh_ika/Downloads/movies'
dst_dir = '/Users/maoh_ika/Downloads/notification'
dst_name_dir = f'{dst_dir}/plate_content/name'
dst_nickname_dir = f'{dst_dir}/plate_content/nickname'
dst_id_dir = f'{dst_dir}/plate_content/id'
dst_plate_dir = f'{dst_dir}/plate'
dst_fullcharge_dir = f'{dst_dir}/fullcharge'
dst_kill_dir = f'{dst_dir}/kill'
dst_char_dir = '/Users/maoh_ika/Downloads/char'
model = YOLO("models/notification/best.pt")
chartype_model = YOLO("models/ocr/char_type/best.pt")
plate_model = YOLO("models/plate/best.pt")
hiragana_model = YOLO("models/ocr/hiragana/best.pt")
katakana_model = YOLO("models/ocr/katakana/best.pt")
number_model = YOLO("models/ocr/number/best.pt")
alphabet_model = YOLO("models/ocr/alphabet/best.pt")
symbol_model = YOLO("models/ocr/symbol/best.pt")
all_model = YOLO("models/ocr/char/best.pt")

char_models = {
    '0': hiragana_model,
    '1': katakana_model,
    '2': number_model,
    '3': alphabet_model,
    '4': symbol_model,
    '5': None,
    '6': None,
    '7': None,
}
    
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

        classes = []
        img_count = 0
        has_rule = False
        for *xyxy, conf, cls in reversed(preds[0]):
            x1 = xyxy[0].numpy().astype('uint')
            y1 = xyxy[1].numpy().astype('uint')
            x2 = xyxy[2].numpy().astype('uint')
            y2 = xyxy[3].numpy().astype('uint')
            cls = int(cls)
            notif_img = img[y1:y2, x1:x2]
            c_x = (x2 + x1) / 2
            c_y = (y2 + y1) / 2
            x = c_x / img.shape[1]
            y = c_y / img.shape[0]
            w = (x2 - x1) / img.shape[1]
            h = (y2 - y1) / img.shape[0]
            box = ' '.join([str(cls), str(x), str(y), str(w), str(h)])
            classes.append(box)
            if cls == 3 and save_plate:
                os.makedirs(dst_name_dir, exist_ok=True)
                os.makedirs(dst_nickname_dir, exist_ok=True)
                os.makedirs(dst_id_dir, exist_ok=True)
                os.makedirs(dst_plate_dir, exist_ok=True)
                img_out = f'{dst_plate_dir}/{out_img_name}_{img_count}.jpg'
                cv2.imwrite(img_out, notif_img)
                #cls_out = f'{dst_plate_dir}/{out_img_name}_{img_count}.txt'
                #detect_chars(notif_img, cls_out)

                player_name_img, player_id_img, nickname_img, notif_boxes = make_plate(plate_model, notif_img)
                if player_name_img is not None and player_name_img.size > 0:
                    img_out = f'{dst_name_dir}/{out_img_name}_{img_count}_name.jpg'
                    cv2.imwrite(img_out, player_name_img)
                    cls_out = f'{dst_name_dir}/{out_img_name}_{img_count}_name.txt'
                    detect_chars(player_name_img, cls_out, out_img_name)
#                if player_id_img is not None and player_id_img.size > 0:
#                    img_out = f'{dst_id_dir}/{out_img_name}_{img_count}_name.jpg'
#                    cv2.imwrite(img_out, player_id_img)
#                    cls_out = f'{dst_id_dir}/{out_img_name}_{img_count}_name.txt'
#                    detect_chars(player_id_img, cls_out, out_img_name)
#                if nickname_img is not None and nickname_img.size > 0:
#                    img_out = f'{dst_nickname_dir}/{out_img_name}_{img_count}_name.jpg'
#                    cv2.imwrite(img_out, nickname_img)
#                    cls_out = f'{dst_nickname_dir}/{out_img_name}_{img_count}_name.txt'
#                    detect_chars(nickname_img, cls_out, out_img_name)
                    
                notif_out = f'{dst_plate_dir}/{out_img_name}_{img_count}.txt'
                f = open(notif_out, 'w')
                for b in notif_boxes:
                    f.write(b + '\n')
                f.close()
                img_count += 1
            elif cls == 0 and save_kill:
                os.makedirs(dst_kill_dir, exist_ok=True)
                img_out = f'{dst_kill_dir}/{out_img_name}_{img_count}.jpg'
                cv2.imwrite(img_out, notif_img)
                cls_out = f'{dst_kill_dir}/{out_img_name}_{img_count}.txt'
                detect_chars(notif_img, cls_out, out_img_name)
            elif cls == 13 and save_fullcharge:
                os.makedirs(dst_fullcharge_dir, exist_ok=True)
                img_out = f'{dst_fullcharge_dir}/{out_img_name}_{img_count}.jpg'
                cv2.imwrite(img_out, notif_img, out_img_name)
            elif cls in [5, 6, 7, 8, 9, 14]:
                has_rule = True

        if len(classes) > 0 and save_notif:
            img_out_path =f'{dst_dir}/{out_img_name}.jpg'
            cv2.imwrite(img_out_path, img)
            classes = sorted(classes, key=lambda b: float(b.split(' ')[1]))
            cls_out = f'{dst_dir}/{out_img_name}.txt'
            f = open(cls_out, 'w')
            for b in classes:
                f.write(b + '\n')
            f.close()
        
        frame += 1