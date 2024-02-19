from ultralytics import YOLO

model = YOLO('yolov8n.pt')

results = model.train(
  cfg=f'/home/maohika/work/ika/train/train_stage_cfg.yaml',
  data='/home/maohika/work/ika/train/train_stage_data.yaml'
)