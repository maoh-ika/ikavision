from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO('yolov8n-cls.pt')
  results = model.train(
    cfg=f'C:/work/ikavision/train/train_buki_cfg.yaml',
    data=f'C:/work/ikavision/dataset/buki'
  )
