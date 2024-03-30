import torch
from ultralytics import YOLO
from models.battle import BattleStage
from prediction.frame_classifier import FrameClassifier
from prediction.frame import Frame
from prediction.prediction_process import preprocess, postprocess
from utils import MovieReader

class StageFrameClassifier:
    def __init__(self,
        battle_movie_path: str,
        model_path: str,
        device: str) -> None:
        dev = torch.device(device)
        self.model = YOLO(model_path)
        self.model.to(dev)
        self.battle_movie_path = battle_movie_path

    def classify(self, frames: list[Frame]) -> dict[int,BattleStage]:
        reader = MovieReader(self.battle_movie_path)
        stage_object_count = {}
        input_batch = []
        for frame in frames:
            img = reader.read(frame.frame)
            input = preprocess(img , self.model.overrides['imgsz'], self.model.device, to_4d=False)
            input_batch.append(input)

        batch_tensor = torch.stack(input_batch)
        preds = self.model.model(batch_tensor)
        preds = postprocess(preds, batch_tensor.shape[2:], img.shape, 0.25, 0.2, 100)
        for pred in preds:
            for *xyxy, conf, cls in pred:
                stage = BattleStage.UNKNOWN
                cls = int(cls.cpu().numpy().astype('uint'))
                if cls == 0: # 'stage_amabi_onion'
                    stage = BattleStage.AMABI
                elif cls == 1: # 'stage_cyozame_drop'
                    stage = BattleStage.CYOUZAME
                elif cls == 2: # 'stage_gonzui_vending_machine'
                    stage = BattleStage.GONZUI
                elif cls == 3: # 'stage_hirame_room'
                    stage = BattleStage.HIRAME
                elif cls == 4: # 'stage_cyozame_crane'
                    stage = BattleStage.CYOUZAME
                elif cls == 5: # 'stage_kinmedai_table'
                    stage = BattleStage.KINMEDAI
                elif cls == 6: # 'stage_kinmedai_center_table'
                    stage = BattleStage.KINMEDAI
                elif cls == 7: # 'stage_konbu_wall'
                    stage = BattleStage.KONBU
                elif cls == 8: # 'stage_kusaya_light'
                    stage = BattleStage.KUSAYA
                elif cls == 9: # 'stage_mahimahi_speaker'
                    stage = BattleStage.MAHIMAHI
                elif cls == 10: # 'stage_mantamaria_mast'
                    stage = BattleStage.MANTAMARIA
                elif cls == 11: # 'stage_mantamaria_rope'
                    stage = BattleStage.MANTAMARIA
                elif cls == 12: # 'stage_masaba_bridge'
                    stage = BattleStage.MASABA
                elif cls == 13: # 'stage_mategai_pillar'
                    stage = BattleStage.MATEGAI
                elif cls == 14: # 'stage_namerou_car'
                    stage = BattleStage.NAMEROU
                elif cls == 15: # 'stage_namerou_truck'
                    stage = BattleStage.NAMEROU
                elif cls == 16: # 'stage_nampula_sheet'
                    stage = BattleStage.NAMPULA
                elif cls == 17: # 'stage_ohyou_head'
                    stage = BattleStage.OHYOU
                elif cls == 18: # 'stage_ohyou_tail'
                    stage = BattleStage.OHYOU
                elif cls == 19: # 'stage_sumeshi_wheel'
                    stage = BattleStage.SUMESHI
                elif cls == 20: # 'stage_sumeshi_rocket'
                    stage = BattleStage.SUMESHI
                elif cls == 21: # 'stage_sumeshi_rail'
                    stage = BattleStage.SUMESHI
                elif cls == 22: # 'stage_takaashi_crane'
                    stage = BattleStage.TAKAASHI
                elif cls == 23: # 'stage_taraport_sculture'
                    stage = BattleStage.TARAPORT
                elif cls == 24: # 'stage_yagara_flag'
                    stage = BattleStage.YAGARA
                elif cls == 25: # 'stage_yunohana_stone'
                    stage = BattleStage.YUNOHANA
                elif cls == 26: # 'stage_zatou_board'
                    stage = BattleStage.ZATOU
                elif cls == 27: # 'stage_kusaya_bamboo'
                    stage = BattleStage.KUSAYA
                elif cls == 28: # 'stage_bangaitei_board'
                    stage = BattleStage.BANGAITEI
                elif cls == 29: # 'stage_negitoro_reel
                    stage = BattleStage.NEGITORO
                elif cls == 30: # 'stage_kaziki_pillar
                    stage = BattleStage.KAZIKI

                if stage != BattleStage.UNKNOWN:
                    if stage not in stage_object_count:
                        stage_object_count[stage] = 1
                    else:
                        stage_object_count[stage] += 1

        reader.release()
        if len(stage_object_count) == 0:
            return None
        else:
            stage_object_count = list(sorted(stage_object_count.items(), key=lambda x: x[1], reverse=True))
            most_lilely_stage = stage_object_count[0][0]
            if len(stage_object_count) == 1:
                return most_lilely_stage
            else:
                most_lilely_count = stage_object_count[0][1]
                second_likely_count = stage_object_count[1][1]
                return most_lilely_stage if second_likely_count * 2 <= most_lilely_count else None
