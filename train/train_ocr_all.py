from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO('yolov8n-cls.pt')
  results = model.train(
    cfg=f'/home/maohika/work/ika/train/train_ocr_all_cfg.yaml',
    data=f'/home/maohika/work/ika/dataset/ocr/all'
    )

