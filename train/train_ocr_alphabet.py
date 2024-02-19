from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO('yolov8n-cls.pt')

  results = model.train(cfg='./train_ocr_alphabet_cfg.yaml')

  print(results)


