from dataclasses import dataclass
from itertools import chain
import concurrent.futures
import time
import cv2
from ultralytics.data.augment import LetterBox
from ultralytics.utils import ops
from ultralytics import YOLO
import numpy as np
import torch
from utils import class_to_dict
from prediction.frame import Frame

@dataclass
class PredictionResultBase:
    frames: list[Frame]
    image_width: int
    image_height: int
    total_frames: int
    start_frame: int
    end_frame: int 
    frame_interval: int
    processing_time: int

    def get_frame(self, frame_number: int) -> Frame:
        if frame_number < self.start_frame or self.end_frame < frame_number:
            return None
        idx = self._index(frame_number)
        if len(self.frames) <= idx:
            return None
        return self.frames[idx]
    
    def get_sliced_frames(self) ->list[Frame]:
        return self.frames[self._index(self.start_frame):self._index(self.end_frame) + 1]
    
    def slice(self, start_frame: int, end_frame: int=None):
        cp = self._copy()
        cp.start_frame = start_frame
        if len(self.frames) > 0:
            end_frame = end_frame if end_frame is not None else self.frames[-1].frame
        else:
            end_frame = start_frame
        cp.end_frame = end_frame
        return cp
    
    def _index(self, frame) -> int:
        base_frame = self.frames[0].frame if len(self.frames) > 0 else 0
        return int((frame - base_frame) / self.frame_interval)
    
    def _copy(self):
        return PredictionResultBase(
            frames=self.frames,
            image_width=self.image_width,
            image_height=self.image_height,
            total_frames=self.total_frames,
            start_frame=self.start_frame,
            end_frame=self.end_frame,
            frame_interval=self.frame_interval,
            processing_time=self.processing_time
        )
    
    def to_dict(self):
        return class_to_dict(self)

def preprocess(img, size, device, to_4d=True):
    img = LetterBox((size, size))(image=img)
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)  # contiguous
    img = torch.from_numpy(img)
    img = img.float()  # uint8 to fp16/32
    img /= 255  # 0 - 255 to 0.0 - 1.0
    img = img.to(device)
    return img.unsqueeze(0) if to_4d else img

def postprocess(preds, model_shape, image_shape, iou_threshold, conf_threshold, max_detections, agnostic=True):
    preds = ops.non_max_suppression(
        preds,
        conf_threshold,
        iou_threshold,
        agnostic=agnostic,
        max_det=max_detections)

    for pred in preds:
        pred[:, :4] = ops.scale_boxes(model_shape, pred[:, :4], image_shape).round()

    return preds

def toCpu(data):
    *xyxy, conf, cls = data 
    x1 = int(xyxy[0].cpu().numpy().astype('uint'))
    y1 = int(xyxy[1].cpu().numpy().astype('uint'))
    x2 = int(xyxy[2].cpu().numpy().astype('uint'))
    y2 = int(xyxy[3].cpu().numpy().astype('uint'))
    conf = float(conf.cpu().numpy().astype('float'))
    cls = int(cls.cpu().numpy().astype('uint'))
    return [x1, y1, x2, y2], conf, cls

def run_prediction(
    name: str,
    battle_movie_path: str,
    model_path: str,
    start_frame: int,
    end_frame: int,
    frame_interval: int,
    device: str,
    batch_size: int,
    iou_threshold: float,
    conf_threshold: float,
    max_detections: int,
    make_frame_result_func,
    make_prediction_completed_func,
    preprocess_func=preprocess,
    postprocesss_func=postprocess,
    tracingEnabled: bool=False
):
    try:
        dev = torch.device(device) 
        model = YOLO(model_path)
        model.to(dev)
        cap = cv2.VideoCapture(battle_movie_path)

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        end_frame = end_frame or total_frames - 1
        
        frame_number = start_frame
        frame_results = []

        progs = { int((end_frame - start_frame) * r) // frame_interval: str(int(r*100)) for r in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]}
        
        print(f'[{name}] process started. total frames: {total_frames}, start: {start_frame}, end: {end_frame}, batch_size: {batch_size}')
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        processing_time = time.time()

        def _predict_batch(batch, frame_numbers):
            if tracingEnabled:
                preds = model.track(batch, persist=True, conf=conf_threshold, iou=iou_threshold, verbose=False, tracker='bytetrack.yaml')
            elif model.task == 'detect':
                batch_tensor = torch.stack(batch)
                preds = model.model(batch_tensor)
                preds = postprocesss_func(preds, batch_tensor.shape[2:], img.shape, iou_threshold, conf_threshold, max_detections)
            elif model.task == 'classify':
                preds = model.predict(torch.stack(batch), verbose=False)
            else:
                raise Exception('invalid task')

            for idx, pred in enumerate(preds):
                frame = make_frame_result_func(pred, frame_numbers[idx], img)
                frame_results.append(frame)

        input_batch = []
        frame_numbers = []
        while True:
            ret = cap.grab()
            if not ret or end_frame < frame_number:
                break
            
            if frame_number % frame_interval != 0:
                frame_number += 1
                continue

            ret, img = cap.retrieve()
            if not ret:
                break

            if tracingEnabled:
                input_batch.append(img)
                frame_numbers.append(frame_number)
            elif model.task == 'detect':
                input = preprocess_func(img, model.overrides['imgsz'], dev, to_4d=False)
                input_batch.append(input)
                frame_numbers.append(frame_number)
            elif model.task == 'classify':
                input = preprocess_func(img, model.overrides['imgsz'], dev, to_4d=False)
                input_batch.append(input)
                frame_numbers.append(frame_number)

            if len(input_batch) == batch_size:
                _predict_batch(input_batch, frame_numbers)
                input_batch = []
                frame_numbers = []

            if frame_number in progs:
                print(f'progress ({name}): {progs[frame_number]}%')

            frame_number += 1
        
        if len(input_batch) > 0:
            _predict_batch(input_batch, frame_numbers)
            input_batch = []
            frame_numbers = []

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        det_result= make_prediction_completed_func(
            width,
            height,
            total_frames,
            start_frame,
            end_frame,
            frame_interval,
            frame_results,
            round(time.time() - processing_time)
        )
        
        print(f'[{name}] process ended. start: {start_frame}, end: {end_frame}, batch_size: {batch_size}')

        return det_result
    except Exception as e:
        print(e)
        return None
    
def run_parallel(
    workers: int,
    name: str,
    battle_movie_path: str,
    model_path: str,
    start_frame: int,
    end_frame: int,
    frame_interval: int,
    device: str,
    batch_size: int,
    iou_threshold: float,
    conf_threshold: float,
    max_detections: int,
    make_frame_result_func,
    make_prediction_completed_func,
    preprocess_func=preprocess,
    postprocesss_func=postprocess,
    tracingEnabled: bool=False
):
    cap = cv2.VideoCapture(battle_movie_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    total_result = PredictionResultBase(
        frames=[],
        image_width=0,
        image_height=0,
        total_frames=total_frames,
        start_frame=0,
        end_frame=0,
        frame_interval=frame_interval,
        processing_time=0
    )
    processing_time = time.time()

    frames_per_worker = total_frames // workers
    total_end_frame = end_frame if end_frame is not None else total_frames - 1
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = []
        for worker_start_frame in range(start_frame, total_end_frame + 1, frames_per_worker + 1):
            worker_end_frame = worker_start_frame + frames_per_worker
            if total_end_frame < worker_end_frame:
                worker_end_frame = total_end_frame
            futures.append(executor.submit(run_prediction,
                name,
                battle_movie_path,
                model_path,
                worker_start_frame,
                worker_end_frame,
                frame_interval,
                device,
                batch_size,
                iou_threshold,
                conf_threshold,
                max_detections,
                make_frame_result_func,
                make_prediction_completed_func,
                preprocess_func,
                postprocesss_func,
                tracingEnabled
            ))

        worker_results = []
        for future in concurrent.futures.as_completed(futures):
            print('')
            result = future.result()
            if len(result.frames) > 0:
                worker_results.append(result)
                
    worker_results.sort(key=lambda r: r.start_frame)
    total_result.frames = list(chain(*list(map(lambda r: r.frames, worker_results))))
    total_result.image_width = worker_results[0].image_width
    total_result.image_height = worker_results[0].image_height
    total_result.start_frame = worker_results[0].start_frame
    total_result.end_frame = worker_results[-1].end_frame
    total_result.processing_time = time.time() - processing_time

    return total_result
