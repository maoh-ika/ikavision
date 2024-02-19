import os
import json
import time
import argparse
from multiprocessing import Event, Process, Value
from dotenv import load_dotenv
from prediction.ikalamp_detection_process import run_ikalamp_detection, SharedIkalampDetectionResult, IkalampDetectionResult
from prediction.ika_player_detection_process import run_ika_player_detection, SharedIkaPlayerDetectionResult, IkaPlayerDetectionResult 
from prediction.notification_detection_process import run_notification_detection, SharedNotificationDetectionResult, NotificationDetectionResult
from prediction.battle_indicator_detection_process import run_battle_indicator_detection, SharedBattleIndicatorDetectionResult, BattleIndicatorDetectionResult
from prediction.match_detection_process import run_match_detection, SharedMatchDetectionResult, MatchDetectionResult 
from player import Player
from battle_analyzer import init, BattleAnalyzer, BattleAnalysisParams, BattlePreprocessParams, ModelPaths
from log import create_prod_logger

load_dotenv()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str)
    parser.add_argument('--process', type=int, default=0)
    return parser.parse_args()

def _run_ikalamp_detection(
    cache_dir: str,
    battle_movie_path: str,
    ikalamp_model_path: str,
    frame_interval: int,
    device: str,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None
):
    file_name = os.path.basename(battle_movie_path)
    ikalamp_cache_path = f'{cache_dir}/{file_name}_ikalamp_{start_frame}_{end_frame}.json'
    if os.path.exists(ikalamp_cache_path):
        with open(ikalamp_cache_path) as f:
            j = json.load(f)
            ikalamp_result = IkalampDetectionResult.from_json(j)
            SharedIkalampDetectionResult.write(ikalamp_result)
    else:
        ikalamp_result = run_ikalamp_detection(
            battle_movie_path=battle_movie_path,
            ikalamp_model_path=ikalamp_model_path,
            frame_interval=frame_interval,
            device=device,
            batch_size=batch_size,
            start_frame=start_frame,
            end_frame=end_frame
        )
        with open(ikalamp_cache_path, 'w') as f:
            ikalamp_result.slice(0)
            json.dump(ikalamp_result.to_dict(), f, indent=2)

    return ikalamp_result

def _run_ika_player_detection(
    cache_dir: str,
    battle_movie_path: str,
    ika_model_path: str,
    frame_interval: int,
    device: str,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None
):
    file_name = os.path.basename(battle_movie_path)
    ika_player_cache_path = f'{cache_dir}/{file_name}_ika_player_{start_frame}_{end_frame}.json'
    if os.path.exists(ika_player_cache_path):
        with open(ika_player_cache_path) as f:
            j = json.load(f)
            ika_player_result = IkaPlayerDetectionResult.from_json(j)
            SharedIkaPlayerDetectionResult.write(ika_player_result)
    else:
        ika_player_result = run_ika_player_detection(
            battle_movie_path=battle_movie_path,
            ika_model_path=ika_model_path,
            frame_interval=frame_interval,
            device=device,
            batch_size=batch_size,
            start_frame=start_frame,
            end_frame=end_frame
        )
        with open(ika_player_cache_path, 'w') as f:
            ika_player_result.slice(0)
            json.dump(ika_player_result.to_dict(), f, indent=2)
    
    return ika_player_result

def _run_notification_detection(
    cache_dir: str,
    battle_movie_path: str,
    notification_model_path: str,
    frame_interval: int,
    device: str,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None
):
    file_name = os.path.basename(battle_movie_path)
    notification_cache_path = f'{cache_dir}/{file_name}_notification_{start_frame}_{end_frame}.json'
    if os.path.exists(notification_cache_path):
        with open(notification_cache_path) as f:
            j = json.load(f)
            notification_result = NotificationDetectionResult.from_json(j)
            SharedNotificationDetectionResult.write(notification_result)
    else:
        notification_result = run_notification_detection(
            battle_movie_path=battle_movie_path,
            notification_model_path=notification_model_path ,
            frame_interval=frame_interval,
            device=device,
            batch_size=batch_size,
            start_frame=start_frame,
            end_frame=end_frame
        )
        with open(notification_cache_path, 'w') as f:
            notification_result.slice(0)
            json.dump(notification_result.to_dict(), f, indent=2)
    
    return notification_result

def _run_battle_indicator_detection(
    cache_dir: str,
    battle_movie_path: str,
    battle_indicator_model_path: str,
    frame_interval: int,
    device: str,
    batch_size: int,
    start_frame: int=0,
    end_frame: int=None
):
    file_name = os.path.basename(battle_movie_path)
    area_cache_path = f'{cache_dir}/{file_name}_battle_indicator_{start_frame}_{end_frame}.json'
    if os.path.exists(area_cache_path):
        with open(area_cache_path) as f:
            j = json.load(f)
            indicator_result = BattleIndicatorDetectionResult.from_json(j)
            SharedBattleIndicatorDetectionResult.write(indicator_result)
    else:
        indicator_result = run_battle_indicator_detection(
            battle_movie_path=battle_movie_path,
            battle_indicator_model_path=battle_indicator_model_path,
            frame_interval=frame_interval,
            device=device,
            batch_size=batch_size,
            start_frame=start_frame,
            end_frame=end_frame
        )
        with open(area_cache_path, 'w') as f:
            indicator_result.slice(0)
            json.dump(indicator_result.to_dict(), f, indent=2)
    
    return indicator_result

class BattleAnalyzerDev(BattleAnalyzer):
    def __init__(self, model_paths: ModelPaths, device: str, log_name: str, cache_dir: str) -> None:
        super().__init__(model_paths, device, log_name)
        self.cache_dir = cache_dir

    def _create_ikalamp_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=_run_ikalamp_detection,
            args=[
                self.cache_dir,
                self.preprocess_params.battle_movie_path,
                self.model_paths.ikalamp_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
   
    def _create_ika_player_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=_run_ika_player_detection,
            args=[
                self.cache_dir,
                self.preprocess_params.battle_movie_path,
                self.model_paths.ika_player_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
    
    def _create_notification_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=_run_notification_detection,
            args=[
                self.cache_dir,
                self.preprocess_params.battle_movie_path,
                self.model_paths.notification_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
    
    def _create_battle_indicator_process(self, frame_interval: int, batch_size: int, start_frame: int, end_frame: int) -> Process:
        return Process(
            target=_run_battle_indicator_detection,
            args=[
                self.cache_dir,
                self.preprocess_params.battle_movie_path,
                self.model_paths.battle_indicator_model_path,
                frame_interval,
                self.device,
                self.preprocess_params.process_id,
                batch_size,
                start_frame,
                end_frame
            ]
        )
    
if __name__ == '__main__':
    args = get_args()
    device = os.environ.get('MODEL_DEVICE')
    
    #battle_movie_path = '/media/maohika/data2/IkaVision/battle_analyzer/movies/splatoon3_environment/2F4Uv4cMkrQ.mp4'
    #battle_movie_path = './videos/test/hoko_knockout.mp4'
#    battle_movie_path = './videos/test/720p_30f_3mbps_192kbps_3btl.mp4'
    battle_movie_path = 'C:/work/ika/temp/EntD9axqHBA/test_hoko_hirame_count_20231210_125811_OH7rilxETp0.mp4'
    #battle_movie_path = "//wsl.localhost/Ubuntu-22.04\mnt\wsl\PHYSICALDRIVE1\IkaVision\dev/battle_analyzer\movies\splatoon3_environment/2u4eZw3cylM.mp4"

    #battle_movie_path = './temp/【スプラトゥーン３】＃８９　毎日ナワバリバトル　金モデラー.mp4'
    model_paths = ModelPaths(
        ikalamp_model_path='./models/ikalamp/best.pt',
        ika_player_model_path='./models/ika/best.pt',
        notification_model_path='./models/notification/best.pt',
        battle_indicator_model_path='./models/battle_indicator/best.pt',
        match_model_path='./models/match/best.pt',
        #map_segment_model_path='./models/map_segment/sumeshi/best.pt',
        plate_model_path='./models/plate/best.pt',
        char_type_model_path='./models/ocr/char_type/best.pt',
        hiragana_model_path='./models/ocr/hiragana/best.pt',
        katakana_model_path='./models/ocr/katakana/best.pt',
        number_model_path='./models/ocr/number/best.pt',
        alphabet_model_path='./models/ocr/alphabet/best.pt',
        symbol_model_path='./models/ocr/symbol/best.pt',
        char_model_path='./models/ocr/char/best.pt',
        stage_model_path='./models/stage/best.pt',
        buki_model_path='./models/buki/best.pt',
        sub_weapon_model_path='./models/sub_weapon/best.pt',
        sp_weapon_model_path='./models/special_weapon/best.pt',
        weapon_gauge_model_path='./models/weapon_gauge/best.pt',
        ink_tank_model_path='./models/ink_tank/best.pt'
    )
    cache_dir=f'./battle_analyzer/logs/{os.path.basename(battle_movie_path)}'
    os.makedirs(cache_dir, exist_ok=True)

    logger = create_prod_logger('battle_analyzer')

    init()
    
    logger.info(f'process id: {args.process}')

#    analyzer = BattleAnalyzerDev(
    analyzer = BattleAnalyzer(
        model_paths=model_paths,
        device=device,
        log_name='battle_analyzer',
#        cache_dir=cache_dir,
    )

    try: 
        preprocess_result = analyzer.preprocess(BattlePreprocessParams(
            battle_movie_path=battle_movie_path,
            analysis_per_second=10,
            batch_size=int(os.environ.get('ANALYSIS_PREPROCESS_BATCH_SIZE')),
            process_id=args.process
        ))

        player = Player(
            ikalamp_model_path=model_paths.ikalamp_model_path,
            ika_model_path=model_paths.ika_player_model_path,
            notification_model_path=model_paths.notification_model_path,
            plate_model_path=model_paths.plate_model_path
        )

        processing_time = time.time()
        analysis_result, _ = analyzer.analyze(BattleAnalysisParams())
        logger.info(f'analyze completed. processing time: {time.time() - processing_time}')
        while analysis_result:
            #player.play(analysis_result)
            processing_time = time.time()
            analysis_result, _ = analyzer.analyze(BattleAnalysisParams(
                start_frame=analysis_result.result_event.end_frame
            ))
            logger.info(f'analyze completed. processing time: {time.time() - processing_time}')
    except Exception as e:
        print(str(e))

    print('################# END #############')
    