from ultralytics import YOLO

if __name__ == '__main__':
  model = YOLO('yolov8n-cls.pt')
  results = model.train(
    cfg=f'/home/maohika/work/ika/train/train_map_segment_sumeshi_cfg.yaml',
    data=f'/home/maohika/work/ika/dataset/map_segment/sumeshi',
    ch=1
    )
