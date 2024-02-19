from dataclasses import dataclass
from threading import Thread
from prediction.ika_player_detection_process import IkaPlayerDetectionResult
from utils import class_to_dict, MovieReader
from models.ika_player import IkaPlayerPosition, IkaPlayerForm
from models.detected_item import TrackableItem
from error import InternalError

@dataclass
class PlayerPositionAnalysisFrame:
    main_player_position: IkaPlayerPosition
    frame: int
    
    @classmethod
    def from_json(cls, j):
        return cls(
            main_player_position=IkaPlayerPosition.from_json(j['main_player_position']),
            frame=j['frame'],
        )
    
@dataclass
class PlayerPositionAnalysisResult:
    frames: list[PlayerPositionAnalysisFrame] 
    
    @classmethod
    def from_json(cls, j):
        return cls(
            frames=[ PlayerPositionAnalysisFrame.from_json(t) for t in j['frames']],
        )
    
    def to_dict(self):
        return class_to_dict(self)

class PlayerPositionFrameAnalyzer(Thread):
    def __init__(self, battle_movie_path: str) -> None:
        super().__init__(name='PlayerPositionFrameAnalyzer')
        self.reader = MovieReader(battle_movie_path)
        self.ika_player_result: IkaPlayerDetectionResult = None
        self.result: PlayerPositionAnalysisResult = None

    def analyze(self, ika_player_result: IkaPlayerDetectionResult) -> PlayerPositionAnalysisResult:
        self.ika_player_result = ika_player_result
        self.start()

    def run(self):
        if self.ika_player_result is None:
            raise InternalError('run must be called via create')
        pos_frames = []
        tracking_positions = {}
        for frame in self.ika_player_result.get_sliced_frames():
            for pos in frame.positions:
                if pos.track_id is None:
                    continue
                if pos.track_id in tracking_positions:
                    # coutinue to track
                    tracking_positions[pos.track_id].append((pos, frame.frame, frame.names))
                else:
                    # found new tracking item
                    tracking_positions[pos.track_id] = [(pos, frame.frame, frame.names)]

        for pos_items in sorted(tracking_positions.values(), key=lambda items: items[0][1]):
            if self._is_main_player_position(pos_items):
                for pos_item in pos_items:
                    pos_frames.append(PlayerPositionAnalysisFrame(pos_item[0], pos_item[1]))

        pos_frames.sort(key=lambda frame: frame.frame)
        self.result = PlayerPositionAnalysisResult(frames=pos_frames)
    
    def _is_main_player_position(self, items: list[(IkaPlayerPosition, int, list[TrackableItem])]) -> bool:
        has_name_frame_count = 0
        for item in items:
            pos, names = item[0], item[2]
            if pos.form == IkaPlayerForm.HITO_FAR: # far position. it likely to be enemy's pos
                return False
            
            for name in names:
                pos_center_y = (pos.xyxy[1] + pos.xyxy[3]) / 2
                if pos.xyxy[1] - 20 <= name.xyxy[3] and name.xyxy[3] <= pos_center_y:
                    name_center_x = (name.xyxy[2] + name.xyxy[0]) / 2
                    if pos.xyxy[0] <= name_center_x and name_center_x <= pos.xyxy[2]:
                        has_name_frame_count += 1
        
        ismain = has_name_frame_count < len(items) * 0.2

        return ismain
