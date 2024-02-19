from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO("yolov8n.pt")

  #results = model.train(cfg="./train_notification_cfg.yaml")
  results = model.train(cfg="/home/maohika/work/ika/train/train_notification_cfg.yaml", data='/home/maohika/work/ika/train/train_notification_data.yaml')

  print(results)

