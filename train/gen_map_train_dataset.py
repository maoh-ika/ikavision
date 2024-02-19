from pathlib import Path
from convert_rgb_to_gray import convert_rgb_gray
from convert_sse_to_yolo import convert_sse_yolo

train_dir = './dataset/map/train'
valid_dir = './dataset/map/valid'
test_dir = './dataset/map/test'

for path in Path('./dataset/map/orig').rglob('*.[jJ][pP][gG]'):
    print(path)
    convert_rgb_gray([str(path)], train_dir)
    convert_sse_yolo([str(path)], train_dir)
