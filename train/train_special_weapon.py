from ultralytics import YOLO

model = YOLO('yolov8n-cls.pt')
results = model.train(
  cfg=f'/home/maohika/work/ika/train/train_special_weapon_cfg.yaml',
  data=f'/home/maohika/work/ika/dataset/special_weapon'
)
