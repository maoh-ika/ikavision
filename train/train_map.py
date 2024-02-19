from ultralytics import YOLO

model = YOLO("yolov8s-seg.pt")

results = model.train(
    batch=2,
    device="cpu",
    data="train_map.yaml",
    epochs=7,
    imgsz=720)

print(results)


