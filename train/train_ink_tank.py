from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO('yolov8s-seg.pt')

  results = model.train(
    cfg='/home/maohika/work/ika/train/train_ink_tank_cfg.yaml',
    data='/home/maohika/work/ika/train/train_ink_tank_data.yaml')

  print(results)

