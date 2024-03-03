import os
from dataclasses import dataclass
import cv2
from dotenv import load_dotenv
import torch
import threading
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator, colors
from prediction.ikalamp_detection_process import make_frame_result as make_ikalamp_frame, make_detection_completed as make_ikalamp_result, IkalampDetectionFrame, IkalampDetectionResult
from prediction.ika_player_detection_process import make_frame_result as make_ika_frame, make_detection_completed as make_ika_result, IkaPlayerDetectionFrame, IkaPlayerDetectionResult
from prediction.prediction_process import run_prediction, preprocess, postprocess
from prediction.player_position_frame_analyzer import PlayerPositionFrameAnalyzer, PlayerPositionAnalysisResult
from prediction.ink_tank_frame_analyzer import InkTankFrameAnalyzer, InkTankAnalysisResult, InkTankAnalysisFrame
from models.ika_player import IkaPlayerPosition
from stream.candle_chart import CandleChart, CandleValue

load_dotenv()

@dataclass
class State:
    frame_number: int
    ikalamp: IkalampDetectionResult = None
    ika: IkaPlayerDetectionResult = None
    main_player_position: PlayerPositionAnalysisResult = None
    ink_tank = InkTankAnalysisResult = None
    ink_tank_chart = CandleChart(candle_count=-1, candle_period=30, fill_with_blank=False)

@dataclass
class InputFrame:
    frame: np.ndarray
    frame_number: int

def draw_bbox(xyxy, label, cls, conf, annotator):
    label =  f'{label} {conf:.2f}'
    annotator.box_label(xyxy, label, color=colors(cls, True))

def draw_ikalamps(ikalamp_frame: IkalampDetectionFrame, annotator: Annotator):
    if ikalamp_frame.team is not None:
        for lamp in ikalamp_frame.team:
            draw_bbox(lamp.xyxy, lamp.state.name, lamp.state.value, lamp.conf, annotator)
    if ikalamp_frame.enemy is not None:
        for lamp in ikalamp_frame.enemy:
            draw_bbox(lamp.xyxy, lamp.state.name, lamp.state.value, lamp.conf, annotator)
    if ikalamp_frame.timer is not None:
        draw_bbox(ikalamp_frame.timer.xyxy, ikalamp_frame.timer.state.name, ikalamp_frame.timer.state.value, ikalamp_frame.timer.conf, annotator)
    
def draw_ika(ika_frame: IkaPlayerDetectionFrame, annotator: Annotator):
    for pos in ika_frame.positions:
        draw_bbox(pos.xyxy, f'{pos.form.name}_{pos.track_id}', pos.form.value, pos.conf, annotator)
    for name in ika_frame.names:
        draw_bbox(name.xyxy, 'name', name.cls, name.conf, annotator)

def draw_main_player(img: np.ndarray, main_player_position: IkaPlayerPosition):
    if main_player_position:
        xyxy = main_player_position.xyxy
        cv2.rectangle(img, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (255, 0, 255), 3)

def draw_ink_tank(img: np.ndarray, ink_tank: InkTankAnalysisFrame):
    if ink_tank.main_player_ink:
        level_x = 0
        level_y = 0
        if ink_tank.main_player_ink.consumed:
            img[ink_tank.main_player_ink.consumed.mask[:, 1], ink_tank.main_player_ink.consumed.mask[:, 0]] = (255,0,0)
            level_x = max(level_x, ink_tank.main_player_ink.consumed.xyxy[2])
            level_y = max(level_y, ink_tank.main_player_ink.consumed.xyxy[3])
        if ink_tank.main_player_ink.remaining:
            img[ink_tank.main_player_ink.remaining.mask[:, 1], ink_tank.main_player_ink.remaining.mask[:, 0]] = (0,0,255)
            level_x = max(level_x, ink_tank.main_player_ink.remaining.xyxy[2])
            level_y = max(level_y, ink_tank.main_player_ink.remaining.xyxy[3])
        level_text = f'{round(ink_tank.main_player_ink.ink_level * 100)}%'
        cv2.putText(img, level_text, (level_x, level_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 4)

def update_frame(state: State, frame: np.ndarray):
    # ゲーム画面にイカランプの枠線を書き込み
    if state.ikalamp:
        ikalamp_frame = state.ikalamp.frames[0]
        ikalamp_annotator = Annotator(frame, line_width=1)
        draw_ikalamps(ikalamp_frame, ikalamp_annotator)
    
    # ゲーム画面にイカタコの枠線を書き込み
    if state.ika:
        ika_frame = state.ika.frames[0]
        ika_annotator = Annotator(frame, line_width=1)
        draw_ika(ika_frame, ika_annotator)

    # 自キャラの枠線を太線で協調表示
    if state.main_player_position and len(state.main_player_position.frames) == 1:
        draw_main_player(frame, state.main_player_position.frames[0].main_player_position)

    # インク残量表示
    if state.ink_tank and len(state.ink_tank.frames) == 1:
        draw_ink_tank(frame, state.ink_tank.frames[0])

def update_ink_tank_chart(state: State, line, ax):
    # グラフの表示期間（フレーム単位）
    x_start = state.frame_number - 3600
    if x_start < 0:
        x_start = 0
    x_end = state.frame_number + 600

    x_data = []
    y_data = []
    for candle in state.ink_tank_chart.candles:
        if candle.start_date <= x_end and candle.end_date >= x_start:
            x_data.append((candle.start_date + candle.end_date) // 2)
            y_data.append(candle.average * 100) # 60フレーム（1秒）の間の平均値を使う
    line.set_xdata(x_data)
    line.set_ydata(y_data)
    ax.set_xlim(x_start, x_end)
    ax.set_ylim(0, 110)
    return line

# AIモデルによる推論実行のプロセス
class PredictionProcess(multiprocessing.Process):
    def __init__(
        self,
        name: str,
        model_path: str,
        request_queue: multiprocessing.Queue,
        result_queue: multiprocessing.Queue,
        frame_interval: int,
        make_frame_func,
        make_result_func) -> None:
        super().__init__(name=name)
        self.model_path = model_path
        self.request_queue = request_queue
        self.result_queue = result_queue
        self.frame_interval = frame_interval
        self.make_frame_func = make_frame_func
        self.make_result_func = make_result_func
        self.shutdown_requested = False
    
    def run(self):
        model = YOLO(self.model_path)
        while not self.shutdown_requested:
            frames = self.request_queue.get()
            images = list(map(lambda f: f.frame, frames))
            preds = self._predict(model, images)
            frame_results = []
            for idx, pred in enumerate(preds):
                frame_result = self.make_frame_func(pred, frames[idx].frame_number, images[idx])
                frame_results.append(frame_result)

            start_frame = frames[0].frame_number
            end_frame = frames[-1].frame_number
            total_frame = end_frame - start_frame + 1
            result = self.make_result_func(
                images[0].shape[1],
                images[-1].shape[0],
                total_frame,
                start_frame,
                end_frame,
                self.frame_interval,
                frame_results,
                0
            )
            self.result_queue.put(result)

    def _predict(self, model: YOLO, frames: list[InputFrame]):
        raise Exception('no impl')
    
# オブジェクト検知モデル実行のプロセス
class DetectionProcess(PredictionProcess):
    def _predict(self, model: YOLO, images: list[np.ndarray]):
        tensors = [preprocess(img, model.overrides['imgsz'], model.device, to_4d=False) for img in images]
        batch = torch.stack(tensors)
        preds = model.model(batch)
        return postprocess(preds, batch.shape[2:], images[0].shape, 0.25, 0.1, 100)

# オブジェクトトラッキングモデル実行のプロセス
class TrackingProcess(PredictionProcess):
    def _predict(self, model: YOLO, images: list[np.ndarray]):
        return model.track(images, persist=True, conf=0.1, iou=0.25, verbose=False, tracker='bytetrack.yaml')

# インク残量推定モデル実行プロセス
class InkTankPredictionProcess(multiprocessing.Process):
    def __init__(self,
        model_path: str,
        device: str,
        request_queue: multiprocessing.Queue,
        result_queue: multiprocessing.Queue
    ):
        super().__init__(name='ink_tank')
        self.model_path = model_path
        self.device = device
        self.request_queue = request_queue
        self.result_queue = result_queue
        self.shutdown_requested = False

    def run(self):
        ink_tank_analyzer = InkTankFrameAnalyzer(
            battle_movie_path=None,
            ink_tank_model_path=self.model_path,
            device=self.device
        )

        while not self.shutdown_requested:
            main_player_position = self.request_queue.get()
            # InkTankFrameAnalyzerをスレッドを使わず実行させるため、runを直接コールする
            ink_tank_analyzer.player_position_result = main_player_position
            ink_tank_analyzer.run()
            self.result_queue.put(ink_tank_analyzer.result)

class ResultMonitorThread(threading.Thread):
    def __init__(self, state: State, result_queue: multiprocessing.Queue, update_func):
        super().__init__()
        self.state = state
        self.result_queue = result_queue
        self.update_func = update_func

    def run(self):
        while True:
            result = self.result_queue.get()
            self.update_func(self.state, result)

class IkaResultMonitor(ResultMonitorThread):
    def __init__(self,
        state: State,
        result_queue: multiprocessing.Queue,
        ink_tank_request_queue: multiprocessing.Queue
    ):
        super().__init__(state, result_queue, self.update)
        self.ink_tank_request_queue = ink_tank_request_queue

    def update(self, state: State, ika_result: IkaPlayerDetectionResult):
        state.ika = ika_result
        # 操作キャラの位置を特定
        # ストリームは1フレームごとに処理するため動画でのバッチ処理に比べて精度は落ちる
        state.main_player_position = player_position_analyzer.analyze(state.ika)
        self.ink_tank_request_queue.put(state.main_player_position)

# インク残量推定の完了監視
class InkTankResultMonitor(ResultMonitorThread):
    def __init__(self, state: State, result_queue: multiprocessing.Queue):
        super().__init__(state, result_queue, self.update)

    def update(self, state: State, ink_tank_result: InkTankAnalysisResult):
        state.ink_tank = ink_tank_result
        if len(ink_tank_result.frames) > 0:
            # インク残量の最新値をグラフに追加
            last_ink_frame = ink_tank_result.frames[-1]
            state.ink_tank_chart.add_value(CandleValue(last_ink_frame.frame, last_ink_frame.main_player_ink.ink_level))

if __name__ == '__main__':
    
    cap = cv2.VideoCapture(1) # この環境ではキャプチャボードのデバイス番号は0
    if not cap.isOpened():
        print('device not found')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # ゲーム画面表示用ウィンドウ
    win_name = 'splatoon3'
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, 1920, 1080)

    # グラフの全体設定
    plt.ion()
    plt.rcParams['toolbar'] = 'None'

    # インク残量グラフ
    fig, ax = plt.subplots()
    line, = ax.plot([], [])
    anim = FuncAnimation(fig, lambda f: update_ink_tank_chart(state, line, ax), frames=[0], interval=100)

    # グラフのスタイル
    plt.gcf().canvas.manager.window.setWindowOpacity(0.5)
    plt.subplots_adjust(left=0.06, right=1, bottom=0.06, top=1)
    plt.get_current_fig_manager().set_window_title('インク残量')
    plt.show()
    
    frame_interval = 10
    device = os.environ.get('MODEL_DEVICE')
    
    state = State(0)

    # イカランプ検出モデル
    ikalamp_model_path = os.environ.get('IKALAMP_MODEL_PATH')
    ikalamp_request_queue = multiprocessing.Queue()
    ikalamp_result_queue = multiprocessing.Queue()
    ikalamp_process = DetectionProcess(
        'ikalamp',
        ikalamp_model_path,
        ikalamp_request_queue,
        ikalamp_result_queue,
        frame_interval,
        make_ikalamp_frame,
        make_ikalamp_result
    )
    ikalamp_process.start()

    # イカタコ検出モデル
    ika_model_path = os.environ.get('IKA_PLAYER_MODEL_PATH')
    ika_request_queue = multiprocessing.Queue()
    ika_result_queue = multiprocessing.Queue()
    ika_process = TrackingProcess(
        'ika',
        ika_model_path,
        ika_request_queue,
        ika_result_queue,
        frame_interval,
        make_ika_frame,
        make_ika_result
    )
    ika_process.start()

    # インク残量推定モデル
    ink_tank_model_path = os.environ.get('INK_TANK_MODEL_PATH')
    ink_tank_request_queue = multiprocessing.Queue()
    ink_tank_result_queue = multiprocessing.Queue()
    ink_tank_process = InkTankPredictionProcess(
        ink_tank_model_path,
        device,
        ink_tank_request_queue,
        ink_tank_result_queue
    )
    ink_tank_process.start()
    
    # 自キャラの位置情報の識別器
    player_position_analyzer = PlayerPositionFrameAnalyzer()

    # イカランプ検出の完了監視
    def _updateIkalamp(state: State, ikalamp_result: IkalampDetectionResult):
        state.ikalamp = ikalamp_result
    ikalamp_update_thread = ResultMonitorThread(state, ikalamp_result_queue, update_func=_updateIkalamp)
    ikalamp_update_thread.start()
    
    # イカタコ位置検出の完了監視
    ika_update_thread = IkaResultMonitor(state, ika_result_queue, ink_tank_request_queue)
    ika_update_thread.start()

    # インク残量推定の完了監視
    ink_tank_update_thread = InkTankResultMonitor(state, ink_tank_result_queue)
    ink_tank_update_thread.start()

    # process stream

    batch_size = 1
    frame_number = 0
    while True:
        state.frame_number = frame_number
        ret, frame = cap.read()
        if not ret:
            print('failed to read frame')
            break
        
        if frame_number % frame_interval != 0:
            frame_number += 1
            update_frame(state, frame)        
            cv2.imshow(win_name, frame)
            cv2.waitKey(1)
            continue
            
        input_batch = []
        input_batch.append(InputFrame(frame, frame_number))

        # イカランプ検出スレッド実行 
        ikalamp_request_queue.put(input_batch)
        # イカタコ検出スレッド実行 
        ika_request_queue.put(input_batch)

        update_frame(state, frame)        
        cv2.imshow(win_name, frame)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

        frame_number += 1

    cap.release()
    cv2.destroyAllWindows() 