from ultralytics import YOLO

if __name__ == '__main__':

  char_types = [
    'all',
#    'hiragana',
    'katakana',
#    'symbol',
#    'number',
#    'alphabet',
#    'greek',
#    'rusian',
]

for ct in char_types:
  model = YOLO('yolov8n-cls.pt')
  results = model.train(
    cfg=f'/home/maohika/work/ika/train/train_ocr_{ct}_cfg.yaml',
    data=f'/home/maohika/work/ika/dataset/ocr/{ct}'
    )
