from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO("yolov8n.pt")

  results = model.train(cfg="/home/maohika/work/ika/train/train_indicator_cfg.yaml", data='/home/maohika/work/ika/train/train_indicator_data.yaml')

  print(results)

