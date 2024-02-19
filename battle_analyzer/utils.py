from enum import Enum
import numpy as np
import cv2
import Levenshtein
from typing import Any
from models.detected_item import DetectedItem
from models.ika_player import IkaPlayer
from prediction.frame import Frame

def class_to_dict(obj):
    # オブジェクトが辞書に変換可能な場合
    if isinstance(obj, Enum):
        return obj.value 
    elif hasattr(obj, "__dict__"):
        result = {}
        for key, value in obj.__dict__.items():
            # 再帰的に変換
            result[key] = class_to_dict(value)
        return result
    # オブジェクトがリストまたはタプルの場合
    elif isinstance(obj, (list, tuple)):
        return [class_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            # 再帰的に変換
            result[key] = class_to_dict(value)
        return result
    # オブジェクトがそのまま返される
    else:
        return obj
    
def hstack(img: np.ndarray=None, items: list[DetectedItem]=None, images: list[np.ndarray]=None) -> np.ndarray:
    def _clip(img: np.ndarray, items: list[DetectedItem]) -> np.ndarray:
        return [img[itm.xyxy[1]:itm.xyxy[3],itm.xyxy[0]:itm.xyxy[2]] for itm in items]
    item_imgs = images if images is not None else _clip(img, items)
    max_w = 0
    max_h = 0
    for item_img in item_imgs:
        if max_h < item_img.shape[0]:
            max_h = item_img.shape[0]
        if max_w < item_img.shape[1]:
            max_w = item_img.shape[1]

    return np.hstack(list(map(lambda img: cv2.resize(img, (max_h, max_w)), item_imgs)))

def bounding_box(mask: np.ndarray):
    non_zero_points = np.transpose(np.nonzero(mask))
    min_x, min_y = np.min(non_zero_points, axis=0)
    max_x, max_y = np.max(non_zero_points, axis=0)
    return [min_x, min_y, max_x, max_y]

class MovieReader:
    def __init__(self, movie_path: str) -> None:
        self.movie_path = movie_path
        self.cap = cv2.VideoCapture(movie_path)
        self.cur_frame = 0
        ret, self.cur_img = self.cap.read()
        if not ret:
            raise Exception('failed to read frame')

    def read(self, frame_number: int) -> np.ndarray:
        if frame_number == self.cur_frame:
            return self.cur_img

        if frame_number < self.cur_frame or (frame_number - self.cur_frame > 100):
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            self.cur_frame = frame_number
            ret, self.cur_img = self.cap.read()
            if not ret:
                raise Exception('failed to read frame')
            #print('MOVIE UNWIND!!!!!!!!!!!!!!!!!')
            return self.cur_img
        else:
            while self.cur_frame < frame_number:
                self.cur_frame += 1
                ret = self.cap.grab()
                if not ret:
                    raise Exception('failed to read frame')
                if self.cur_frame == frame_number:
                    ret, self.cur_img = self.cap.retrieve()
                    if not ret:
                        raise Exception('failed to read frame')
            return self.cur_img
    
    def release(self):
        self.cap.release()

def is_likely_equal(test_str: str, target_str: str) -> bool:
    return Levenshtein.ratio(test_str, target_str) > 0.5

def are_overlapping(xyxy1: list[int], xyxy2: list[int]) -> bool:
    l1, r1, b1, t1 = xyxy1[0], xyxy1[2], xyxy1[1], xyxy1[3]
    l2, r2, b2, t2 = xyxy2[0], xyxy2[2], xyxy2[1], xyxy2[3]

    return (l1 < r2 and l2 < r1 and b1 < t2 and b2 < t1)

def choice_frames(frames: list[Frame], size: int, cond=lambda f: True) -> list[Frame]:
    choices = [frames[idx] for idx in np.random.choice(len(frames), size, replace=False) if cond(frames[idx])]
    choices.sort(key=lambda f: f.frame)
    return choices

def likely_value(values: list[Any], to_value=None) -> Any:
    value_counts = {}
    for value in values:
        val = to_value(value) if to_value else value
        if val is not None:
            if val not in value_counts:
                value_counts[val] = 1
            else:
                value_counts[val] += 1

    if len(value_counts) == 0:
        return None
    
    value_counts = list(sorted(value_counts.items(), key=lambda x: x[1], reverse=True))
    return value_counts[0][0]

def calc_similarity(value: str, target: str) -> float:
    return Levenshtein.ratio(value, target)


def find_one(lst, condition):
    for i, item in enumerate(lst):
        if condition(item):
            return i, item
    return None, None

def normalized_levenshtein_distance(s1: str, s2: str) -> float:
    len_s1 = len(s1)
    len_s2 = len(s2)
    distance = Levenshtein.ratio(s1, s2)
    normalized_distance = distance / max(len_s1, len_s2)
    return normalized_distance