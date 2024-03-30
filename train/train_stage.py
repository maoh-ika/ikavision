from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO('yolov8n.pt')
  save = './out'

  results = model.train(
    cfg=f'C:/work/ikavision/train/train_stage_cfg.yaml',
    data='C:/work/ikavision/train/train_stage_data.yaml',
    project=save
  )