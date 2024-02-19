from dataclasses import dataclass
import torch
import numpy as np
from ultralytics import YOLO
from models.buki import MainWeapon
from models.ikalamp import IkalampState, Ikalamp
from prediction.frame import Frame
from prediction.ika_player_detection_process import IkaPlayerDetectionFrame
from utils import MovieReader

cls_buki_map = {
    'bold_marker': MainWeapon.BOLD_MARKER,
    'bold_marker_neo': MainWeapon.BOLD_MARKER_NEO,
    'wakaba_shooter': MainWeapon.WAKABA_SHOOTER,
    'momiji_shooter': MainWeapon.MOMIJI_SHOOTER,
    'promodeler_mg': MainWeapon.PROMODELER_MG,
    'promodeler_rg': MainWeapon.PROMODELER_RG,
    'sharp_marker': MainWeapon.SHARP_MARKER,
    'sharp_marker_neo': MainWeapon.SHARP_MARKER_NEO,
    'spla_shooter': MainWeapon.SPLA_SHOOTER,
    'hero_shooter_replica': MainWeapon.HERO_SHOOTER_REPLICA,
    'spla_shooter_collabo': MainWeapon.SPLA_SHOOTER_COLLABO,
    'nzap85': MainWeapon.NZAP85,
    'nzap89': MainWeapon.NZAP89,
    '52gallon': MainWeapon._52GALLON,
    'prime_shooter': MainWeapon.PRIME_SHOOTER,
    'prime_shooter_collabo': MainWeapon.PRIME_SHOOTER_COLLABO,
    '96gallon': MainWeapon._96GALLON,
    '96gallon_deco': MainWeapon._96GALLON_DECO,
    'jet_sweeper': MainWeapon.JET_SWEEPER,
    'jet_sweeper_custom': MainWeapon.JET_SWEEPER_CUSTOM,
    'space_shooter': MainWeapon.SPACE_SHOOTER,
    'space_shooter_collabo': MainWeapon.SPACE_SHOOTER_COLLABO,
    'l3_reelgun': MainWeapon.L3_REELGUN,
    'l3_reelgun_d': MainWeapon.L3_REELGUN_D,
    'h3_reelgun': MainWeapon.H3_REELGUN,
    'h3_reelgun_d': MainWeapon.H3_REELGUN_D,
    'bottole_kaiser': MainWeapon.BOTTOLE_KAISER,
    'carbon_roller': MainWeapon.CARBON_ROLLER,
    'carbon_roller_deco': MainWeapon.CARBON_ROLLER_DECO,
    'spla_roller': MainWeapon.SPLA_ROLLER,
    'spla_roller_collabo': MainWeapon.SPLA_ROLLER_COLLABO,
    'dynamo_roller': MainWeapon.DYNAMO_ROLLER,
    'dynamo_roller_tesla': MainWeapon.DYNAMO_ROLLER_TESLA,
    'variable_roller': MainWeapon.VARIABLE_ROLLER,
    'wide_roller': MainWeapon.WIDE_ROLLER,
    'wide_roller_collabo': MainWeapon.WIDE_ROLLER_COLLABO,
    'classic_squiffer': MainWeapon.CLASSIC_SQUIFFER,
    'spla_charger': MainWeapon.SPLA_CHARGER,
    'spla_scope': MainWeapon.SPLA_SCOPE,
    'spla_charger_collabo': MainWeapon.SPLA_CHARGER_COLLABO,
    'spla_scope_collabo': MainWeapon.SPLA_SCOPE_COLLABO,
    'eliter_4k': MainWeapon.ELITER_4K,
    '4k_scope': MainWeapon._4K_SCOPE,
    '14shiki_takedutsu_kou': MainWeapon._14SHIKI_TAKEDUTSU_KOU,
    'soy_tuber': MainWeapon.SOY_TUBER,
    'soy_tuber_custom': MainWeapon.SOY_TUBER_CUSTOM,
    'rpen_5h': MainWeapon.RPEN_5H,
    'nova_blaster': MainWeapon.NOVA_BLASTER,
    'nova_blaster_neo': MainWeapon.NOVA_BLASTER_NEO,
    'hot_blaster': MainWeapon.HOT_BLASTER,
    'long_blaster': MainWeapon.LONG_BLASTER,
    'rapid_blaster': MainWeapon.RAPID_BLASTER,
    'rapid_blaster_deco': MainWeapon.RAPID_BLASTER_DECO,
    'r_blaster_elite': MainWeapon.R_BLASTER_ELITE,
    'r_blaster_elite_deco': MainWeapon.R_BLASTER_ELITE_DECO,
    'crash_blaster': MainWeapon.CRASH_BLASTER,
    'crash_blaster_neo': MainWeapon.CRASH_BLASTER_NEO,
    'sblast92': MainWeapon.SBLAST92,
    'hissen': MainWeapon.HISSEN,
    'hissen_nouveau': MainWeapon.HISSEN_NOUVEAU,
    'bucket_slosher': MainWeapon.BUCKET_SLOSHER,
    'bucket_slosher_deco': MainWeapon.BUCKET_SLOSHER_DECO,
    'screw_slosher': MainWeapon.SCREW_SLOSHER,
    'screw_slosher_neo': MainWeapon.SCREW_SLOSHER_NEO,
    'over_flosher': MainWeapon.OVER_FLOSHER,
    'over_flosher_deco': MainWeapon.OVER_FLOSHER_DECO,
    'explosher': MainWeapon.EXPLOSHER,
    'spla_spiner': MainWeapon.SPLA_SPINER,
    'spla_spiner_collabo': MainWeapon.SPLA_SPINER_COLLABO,
    'barrel_spiner': MainWeapon.BARREL_SPINER,
    'barrel_spiner_deco': MainWeapon.BARREL_SPINER_DECO,
    'hydrant': MainWeapon.HYDRANT,
    'kugelschreiber': MainWeapon.KUGELSCHREIBER,
    'kugelschreiber_nouveau': MainWeapon.KUGELSCHREIBER_NOUVEAU,
    'nautilus47': MainWeapon.NAUTILUS47,
    'pablo': MainWeapon.PABLO,
    'pablo_nouveau': MainWeapon.PABLO_NOUVEAU,
    'hokusai': MainWeapon.HOKUSAI,
    'hokusai_nouveau': MainWeapon.HOKUSAI_NOUVEAU,
    'vincent': MainWeapon.VINCENT,
    'dapple_dualies': MainWeapon.DAPPLE_DUALIES,
    'dapple_dualies_nouveau': MainWeapon.DAPPLE_DUALIES_NOUVEAU,
    'spla_maneuver': MainWeapon.SPLA_MANEUVER,
    'dual_sweeper': MainWeapon.DUAL_SWEEPER,
    'dual_sweeper_custom': MainWeapon.DUAL_SWEEPER_CUSTOM,
    'kelvin535': MainWeapon.KELVIN535,
    'quad_hopper_black': MainWeapon.QUAD_HOPPER_BLACK,
    'quad_hopper_white': MainWeapon.QUAD_HOPPER_WHITE,
    'para_shelter': MainWeapon.PARA_SHELTER,
    'para_shelter_solare': MainWeapon.PARA_SHELTER_SOLARE,
    'camping_shelter': MainWeapon.CAMPING_SHELTER,
    'camping_shelter_solare': MainWeapon.CAMPING_SHELTER_SOLARE,
    'spy_gadget': MainWeapon.SPY_GADGET,
    'tri_stringer': MainWeapon.TRI_STRINGER,
    'tri_stringer_collabo': MainWeapon.TRI_STRINGER_COLLABO,
    'lact450': MainWeapon.LACT450,
    'drive_wiper': MainWeapon.DRIVE_WIPER,
    'drive_wiper_deco': MainWeapon.DRIVE_WIPER_DECO,
    'gym_wiper': MainWeapon.GYM_WIPER,
    'examiner': MainWeapon.EXAMINER,
    'moplin': MainWeapon.MOPLIN,
    'bottole_kaiser_foil': MainWeapon.BOTTOLE_KAISER_FOIL,
    'gym_wiper_nouveau': MainWeapon.GYM_WIPER_NOUVEAU,
    'hot_blaster_custom': MainWeapon.HOT_BLASTER_CUSTOM,
    'lact450_deco': MainWeapon.LACT450_DECO,
    'rpen_5b': MainWeapon.RPEN_5B,
    'sblast91': MainWeapon.SBLAST91,
    'spla_maneuver_collabo': MainWeapon.SPLA_MANEUVER_COLLABO,
    'spy_gadget_solare': MainWeapon.SPY_GADGET_SOLARE,
    'vincent_nouveau': MainWeapon.VINCENT_NOUVEAU
}

@dataclass
class BukClassificationFrame(Frame):
    team_mains: list[MainWeapon]
    enemy_mains: list[MainWeapon]

class BukiFrameClassifier:
    def __init__(self,
        battle_movie_path: str,
        model_path: str,
        device: str) -> None:
        dev = torch.device(device)
        self.model = YOLO(model_path)
        self.model.to(dev)
        self.battle_movie_path = battle_movie_path
    
    def classify_most_likely(self, frames: list[Frame]) -> (list[MainWeapon], list[MainWeapon]):
        if len(frames) == 0:
            return None
        predicts = self.classify(frames)
        team_main_counts: list[dict[MainWeapon,int]] = []
        enemy_main_counts: list[dict[MainWeapon,int]] = []
        for buki_frame in predicts.values():
            if len(team_main_counts) == 0:
                team_main_counts = [{} for _ in range(len(buki_frame.team_mains))]
            if len(enemy_main_counts) == 0:
                enemy_main_counts = [{} for _ in range(len(buki_frame.enemy_mains))]
            for ord, team_main in enumerate(buki_frame.team_mains):
                if team_main != MainWeapon.UNKNOWN:
                    if team_main not in team_main_counts[ord]:
                        team_main_counts[ord][team_main] = 1
                    else:
                        team_main_counts[ord][team_main] += 1
            for ord, enemy_main in enumerate(buki_frame.enemy_mains):
                if enemy_main != MainWeapon.UNKNOWN:
                    if enemy_main not in enemy_main_counts[ord]:
                        enemy_main_counts[ord][enemy_main] = 1
                    else:
                        enemy_main_counts[ord][enemy_main] += 1

        team_mains_likely = []
        for main_count in team_main_counts:
            sorted_count = list(sorted(main_count.items(), key=lambda x: x[1], reverse=True))
            team_mains_likely.append(sorted_count[0][0])

        enemy_mains_likely = []
        for main_count in enemy_main_counts:
            sorted_count = list(sorted(main_count.items(), key=lambda x: x[1], reverse=True))
            enemy_mains_likely.append(sorted_count[0][0])

        return (team_mains_likely, enemy_mains_likely)

    def classify(self, frames: list[IkaPlayerDetectionFrame]) -> dict[int, BukClassificationFrame]:
        reader = MovieReader(self.battle_movie_path)
        def _predict(lamp: Ikalamp, img: np.ndarray) -> MainWeapon:
            if lamp.state in [IkalampState.DEATH, IkalampState.DROP]:
                return MainWeapon.UNKNOWN
            lamp_img = img[lamp.xyxy[1]:lamp.xyxy[3],lamp.xyxy[0]:lamp.xyxy[2]]
            res = self.model.predict(lamp_img, verbose=False)[0]
            cls = res.names[res.probs.top1]
            return cls_buki_map[cls] if cls in cls_buki_map else MainWeapon.UNKNOWN

        buki_frames = {}
        for frame in frames:
            img = reader.read(frame.frame)
            team_mains = []
            for lamp in frame.team:
                main = _predict(lamp, img)
                team_mains.append(main)
            enemy_mains = []
            for lamp in frame.enemy:
                main = _predict(lamp, img)
                enemy_mains.append(main)
            buki_frames[frame.frame] = BukClassificationFrame(
                frame=frame.frame,
                team_mains=team_mains,
                enemy_mains=enemy_mains,
                image=None
            )

        reader.release()

        return buki_frames