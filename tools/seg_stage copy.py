import time
from ultralytics import YOLO
import torch
import cv2
from ultralytics.data.augment import LetterBox
from ultralytics.utils.plotting import Annotator, colors
from ultralytics.utils import ops
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt

def preprocess(img, size=640):
    img = LetterBox(size, True)(image=img)
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
#    img = np.ascontiguousarray(img)  # contiguous
    img = torch.from_numpy(img)
    img = img.float()  # uint8 to fp16/32
#    img /= 255  # 0 - 255 to 0.0 - 1.0
    return img.unsqueeze(0)

def postprocess(preds, img, orig_img):
    preds = ops.non_max_suppression(preds,
                                    0.25,
                                    0.8,
                                    agnostic=False,
                                    max_det=100)

    for i, pred in enumerate(preds):
        shape = orig_img.shape
        pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

    return preds

def draw_bbox(boxes, names, annotator):
    for idx in range(len(boxes.data)):
        cls = int(boxes.cls[idx])  # integer class
        label =  f'{names[cls]} {float(boxes.conf[idx]):.2f}'
        annotator.box_label(boxes.data[idx], label, color=colors(cls, True))

def detect_stage(model, frame, conf_thr):
  result = stage_seg_model.predict(frame, retina_masks=True)[0]
  if len(result.boxes.data) == 0:
    return None
  
  # stage box index
  stage_mask = np.zeros([frame.shape[0], frame.shape[1], 1], np.uint8)
  for idx in range(len(result.masks.data)):
    if result.boxes.conf[idx] >= conf_thr:
      stage_mask =  cv2.bitwise_or(result.masks.data[idx].numpy().astype('uint8'), stage_mask)
  stage_image = cv2.bitwise_and(frame, frame ,mask=stage_mask)
  stage_image = cv2.cvtColor(cv2.cvtColor(stage_image, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB)
  return (stage_image, stage_mask)
   

#stage_seg_model = YOLO('runs/segment/train/weights/best.pt', task='segment')
#bs = cv2.createBackgroundSubtractorMOG2()
bs = cv2.bgsegm.createBackgroundSubtractorMOG(history=10)

#cap = cv2.VideoCapture("./videos/2023062516564700-4CE9651EE88A979D41F24CE8D6EA1C23.mp4")
cap = cv2.VideoCapture(0)
fps = round(cap.get(cv2.CAP_PROP_FPS))
wait_secs = int(1000 / fps)


n = 0
stage_mask = None
stage_image = None
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
while True:
    ret, frame = cap.read()
    if not ret:
        cv2.waitKey(wait_secs)
        continue
    n += 1
    
    cv2.imshow('cur frame', frame)
    
#    if n % fps != 0:
#        n += 1
#        shoot_mask = bs.apply(frame)
#        cv2.waitKey(wait_secs)
#        continue
    
    H,W,_ = frame.shape

    # RGBからHSVへの変換
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 色の範囲を定義 (例: 緑色)

    # 黄色
    lower = np.array([25, 100, 100])  # 下限 (H, S, V)
    upper = np.array([30, 255, 255])  # 上限 (H, S, V)

    # ピンク 
    #lower = np.array([140, 50, 50])  # 下限 (H, S, V)
    #upper = np.array([180, 255, 255])  # 上限 (H, S, V)

    # 指定した色範囲のマスクを作成
    mask = cv2.inRange(hsv_image, lower, upper)
    masked_image = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("masked frame", masked_image)
    #mask = cv2.bitwise_not(mask)
    
    frame_detect = bs.apply(masked_image)
   
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))  # カーネルサイズを調整
    frame_detect_denoise = cv2.morphologyEx(frame_detect, cv2.MORPH_OPEN, kernel)
    
    cv2.imshow("detect", frame_detect)
    cv2.imshow("detect_denoise", frame_detect_denoise)
    cv2.waitKey(wait_secs)

cap.release()
cv2.destroyAllWindows()
exit(0)

img = cv2.imread('./images/temp/IMG_4142.JPG')
img2 = cv2.imread('./images/temp/IMG_4143.JPG')

H,W,_ = img.shape

shoot_mask = bs.apply(img)
shoot_mask = bs.apply(img2)
cv2.imshow("shoot mask", shoot_mask)
    
origin = deepcopy(img)
#img = preprocess(img)
annotator = Annotator(origin, line_width=1, example=str(model.model.names))
result = stage_seg_model.predict(img, retina_masks=True)[0]

# stage box index
max_idx = result.boxes.conf.numpy().argmax()
stage_mask = result.masks.data[max_idx]
cv2.imshow("stage mask", stage_mask.numpy())

# apply masks
masked = cv2.bitwise_and(img2, img2 ,mask=stage_mask.numpy().astype('uint8'))
masked = cv2.bitwise_and(masked, masked, mask=shoot_mask.astype('uint8'))
cv2.imshow('masked shoot', masked)

# seg border 
#x = (result.masks.segments[0][:,0]*W).astype("int")
#y = (result.masks.segments[0][:,1]*H).astype("int")
#blk=np.zeros((H,W))
#blk[y,x] =255
#cv2.imshow('m', blk.astype("uint8"))
cv2.waitKey(0)

mask_img = result.masks.data[max_idx]
mask_seg = ops.masks2segments(result.masks.data)[max_idx]
cv2.imwrite('./test.jpg', result.masks.xy[max_idx])

seg = result.masks.xy[max_idx]
annotator.box_label(seg, 's')


#draw_bbox(result.boxes, model.names, annotator)
masks = result.masks  # Masks object for segmentation masks outputs

cv2.imshow("test",origin)
cv2.waitKey(0)
cv2.destroyAllWindows()
