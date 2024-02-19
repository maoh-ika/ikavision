from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO("yolov8n.pt")

  results = model.train(cfg="/home/maohika/work/ika/train/train_weapon_gauge_cfg.yaml", data='/home/maohika/work/ika/train/train_weapon_gauge_data.yaml')

  print(results)

