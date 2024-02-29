from dataclasses import dataclass
from threading import Thread
from prediction.ika_player_detection_process import IkaPlayerDetectionResult
from utils import class_to_dict
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

# キャラクタの位置情報から、自キャラを識別する
class PlayerPositionFrameAnalyzer:
    def analyze(self, ika_player_result: IkaPlayerDetectionResult) -> PlayerPositionAnalysisResult:
        # 自キャラが検出されたフレームリスト
        pos_frames = []
        # トラッキングIDごとにグループ化したキャラクタ位置情報リスト
        # リストの要素は(位置情報、フレーム番号、フレーム画像内のプレイヤー名オブジェクトリスト)のタプル
        tracking_positions = {}
        for frame in ika_player_result.get_sliced_frames():
            for pos in frame.positions:
                if pos.track_id is None: # トラッキングIDが無いオブジェクトは検知ミスの可能性が高いので無視
                    continue
                if pos.track_id in tracking_positions:
                    # coutinue to track
                    tracking_positions[pos.track_id].append((pos, frame.frame, frame.names))
                else:
                    # found new tracking item
                    tracking_positions[pos.track_id] = [(pos, frame.frame, frame.names)]

        # トラッキングIDごとに、位置情報が自キャラのものか判定
        for pos_items in sorted(tracking_positions.values(), key=lambda items: items[0][1]): # フレーム番号で昇順ソート
            if self._is_main_player_position(pos_items):
                for pos_item in pos_items:
                    pos_frames.append(PlayerPositionAnalysisFrame(pos_item[0], pos_item[1]))

        # 自キャラが検出されたフレームだけを、自キャラの位置情報と一緒に返す
        pos_frames.sort(key=lambda frame: frame.frame)
        return PlayerPositionAnalysisResult(frames=pos_frames)

    # 位置情報が自キャラのものか判定 
    def _is_main_player_position(self, items: list[(IkaPlayerPosition, int, list[TrackableItem])]) -> bool:
        has_name_frame_count = 0
        for item in items:
            pos, names = item[0], item[2]
            if pos.form == IkaPlayerForm.HITO_FAR: # far position. it likely to be enemy's pos
                return False

            # キャラの位置を示す矩形の頭上に、一定範囲内でプレイヤー名オブジェクトが存在しているフレームの数をカウント 
            for name in names:
                pos_center_y = (pos.xyxy[1] + pos.xyxy[3]) / 2
                if pos.xyxy[1] - 20 <= name.xyxy[3] and name.xyxy[3] <= pos_center_y:
                    name_center_x = (name.xyxy[2] + name.xyxy[0]) / 2
                    if pos.xyxy[0] <= name_center_x and name_center_x <= pos.xyxy[2]:
                        has_name_frame_count += 1
        
        # 位置矩形の頭上にプレイヤー名があったフレームが一定数未満であれば自キャラと判断する
        # 複数のフレームに渡って判定することで自キャラと他キャラが一時的に重なり合う状況での判定ミスを軽減する
        ismain = has_name_frame_count < len(items) * 0.2

        return ismain
