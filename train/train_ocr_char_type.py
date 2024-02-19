from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO("yolov8s.pt")

  results = model.train(cfg="/home/maohika/work/ika/train/train_ocr_char_type_cfg.yaml", data='/home/maohika/work/ika/train/train_ocr_char_type_data.yaml')

  print(results)

