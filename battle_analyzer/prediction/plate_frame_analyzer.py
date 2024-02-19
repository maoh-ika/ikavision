from dataclasses import dataclass
import torch
from ultralytics import YOLO
from models.text import Text, Char
from models.plate import Plate, Badge
from models.notification import NotificationType
from prediction.notification_detection_process import NotificationDetectionFrame
from prediction.prediction_process import preprocess, postprocess
from prediction.splash_font_ocr import SplashFontOCR
from utils import class_to_dict, MovieReader

@dataclass
class PlateAnalysisFrame:
    plates: [Plate]
    frame: int
    
    @classmethod
    def from_json(cls, j):
        return cls(
            plates=[Plate.from_json(t) for t in j['plates']],
            frame=j['frame']
        )
    
@dataclass
class PlateAnalysisResult:
    frames: list[PlateAnalysisFrame]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            frames=[PlateAnalysisFrame.from_json(t) for t in j['frames']]
        )
    
    def to_dict(self):
        return class_to_dict(self)

class PlateFrameAnalyzer:
    def __init__(self,
            plate_model_path: str,
            battle_movie_path: str,
            ocr: SplashFontOCR, 
            device: str
        ) -> None:
        dev = torch.device(device)
        self.plate_model = YOLO(plate_model_path)
        self.plate_model.to(dev)
        self.ocr = ocr
        self.reader = MovieReader(battle_movie_path)

    def analyze(self,
        frames: [NotificationDetectionFrame],
        ignore_name: bool=False,
        ignore_nickname: bool=False,
        ignore_id: bool=False,
        ignore_badge: bool=False
    ) -> PlateAnalysisResult:
        plate_frames = []
        for frame in frames:
            plate_notifs = list(filter(lambda n: n.type == NotificationType.NOTIFICATION_PLAYER_PLATE, frame.notifications))
            if len(plate_notifs) == 0:
                continue
            img = self.reader.read(frame.frame)
            plates = []
            for notif in plate_notifs:
                plate_img = img[notif.xyxy[1]:notif.xyxy[3], notif.xyxy[0]:notif.xyxy[2]]
                plate = self.make_plate(plate_img, notif.xyxy, notif.conf, notif.cls, ignore_name, ignore_nickname, ignore_id, ignore_badge)
                if plate is not None:
                    plates.append(plate)
            plate_frames.append(PlateAnalysisFrame(plates=plates, frame=frame.frame))
        
        plate_frames.sort(key=lambda frame: frame.frame)
        result = PlateAnalysisResult(frames=plate_frames)
        
        return result

    def make_plate(self,
        plate_img,
        plate_xyxy,
        plate_conf,
        plate_cls,
        ignore_name: bool,
        ignore_nickname: bool,
        ignore_id: bool,
        ignore_badge: bool
    ) -> Plate:
        input = preprocess(plate_img, self.plate_model.overrides['imgsz'], self.plate_model.device)
        preds = self.plate_model.model(input)
        pred = postprocess(preds, input.shape[2:], plate_img.shape, 0.25, 0.2, 10)[0]
        pred = sorted(pred, key=lambda p: p[0]) # sort with x
        player_id = None
        player_name = None
        nickname = None
        badges = []
        offset_x = plate_xyxy[0]
        offset_y = plate_xyxy[1]
        for *xyxy, conf, cls in pred:
            x1 = int(xyxy[0].cpu().numpy().astype('uint'))
            y1 = int(xyxy[1].cpu().numpy().astype('uint'))
            x2 = int(xyxy[2].cpu().numpy().astype('uint'))
            y2 = int(xyxy[3].cpu().numpy().astype('uint'))
            conf = float(conf.cpu().numpy().astype('float'))
            cls = int(cls.cpu().numpy().astype('uint'))
            box_abs = [x1 + offset_x, y1 + offset_y, x2 + offset_x, y2 + offset_y] # to play image coordinate
            content_img = plate_img[y1:y2,x1:x2]
            if cls == 0:
                text  = Text(value=self.get_text(content_img, offset_x + x1, offset_y + y1), xyxy=box_abs, conf=conf, cls=cls) if not ignore_name else None
                if player_name is None:
                    player_name = text
                else:
                    player_name.concat(text)
            elif cls == 1:
                text = Text(value=self.get_text(content_img, offset_x + x1, offset_y + y1), xyxy=box_abs, conf=conf, cls=cls) if not ignore_id else None
                if player_id is None:
                    player_id = text
                else:
                    player_id.concat(text)
            elif cls == 2:
                text = Text(value=self.get_text(content_img, offset_x + x1, offset_y + y1), xyxy=box_abs, conf=conf, cls=cls) if not ignore_nickname else None
                if nickname is None:
                    nickname = text
                else:
                    nickname.concat(text)
            elif cls == 3:
                badge = Badge(xyxy=box_abs, conf=conf, cls=cls) if not ignore_badge else None
                badges.append(badge)
            else:
                return None

        return Plate(
            player_id=player_id,
            player_name=player_name,
            nickname=nickname,
            badges=badges,
            xyxy=plate_xyxy,
            conf=plate_conf,
            cls=plate_cls
        )
    
    def get_text(self, img, offset_x, offset_y) -> list[Char]:
        chars = self.ocr.get_text(img)
        for c in chars:
            c.xyxy[0] += offset_x
            c.xyxy[1] += offset_y
            c.xyxy[2] += offset_x
            c.xyxy[3] += offset_y
        return chars
