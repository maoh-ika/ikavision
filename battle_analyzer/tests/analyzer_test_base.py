import unittest
import os
from multiprocessing import Process
from dotenv import load_dotenv
import Levenshtein
from error import ErrorCode
from battle_analyzer import BattleAnalyzer, BattleAnalysisParams, BattlePreprocessParams, ModelPaths, BattleAnalysisResult, BattlePreprocessResult
from run_player import BattleAnalyzerDev
from tests.battle_timer import BattleTimer
from models.battle import BattleRule, BattleSide, BattleStage, BattleWinLose
from models.ika_player import IkaPlayer
from models.ink_color import InkColor
from models.buki import Buki
from events.kill_event import KillEvent
from events.death_event import DeathEvent
from events.special_weapon_event import SpecialWeaponEvent
from prediction.shared_memory import SharedMemory
from utils import class_to_dict
from log import create_prod_logger

load_dotenv()

class SharedPrepressResult(SharedMemory):
    SHM_NAME = 'shared_prepress_result'

class SharedAnalysisResult(SharedMemory):
    SHM_NAME = 'shared_analysis_result'

def get_model_paths() -> ModelPaths:
    return ModelPaths(
        ikalamp_model_path=os.environ.get('IKALAMP_MODEL_PATH'),
        ika_player_model_path=os.environ.get('IKA_PLAYER_MODEL_PATH'),
        notification_model_path=os.environ.get('NOTIFICATION_MODEL_PATH'),
        plate_model_path=os.environ.get('PLATE_MODEL_PATH'),
        battle_indicator_model_path=os.environ.get('BATTLE_INDICATOR_MODEL_PATH'),
        match_model_path=os.environ.get('MATCH_MODEL_PATH'),
        char_type_model_path=os.environ.get('CHAR_TYPE_MODEL_PATH'),
        hiragana_model_path=os.environ.get('HIRAGANA_MODEL_PATH'),
        katakana_model_path=os.environ.get('KATAKANA_MODEL_PATH'),
        number_model_path=os.environ.get('NUMBER_MODEL_PATH'),
        alphabet_model_path=os.environ.get('ALPHABET_MODEL_PATH'),
        symbol_model_path=os.environ.get('SYMBOL_MODEL_PATH'),
        char_model_path=os.environ.get('CHAR_MODEL_PATH'),
        stage_model_path=os.environ.get('STAGE_MODEL_PATH'),
        buki_model_path=os.environ.get('BUKI_MODEL_PATH'),
        sub_weapon_model_path=os.environ.get('SUB_WEAPON_MODEL_PATH'),
        sp_weapon_model_path=os.environ.get('SPECIAL_WEAPON_MODEL_PATH'),
        weapon_gauge_model_path=os.environ.get('WEAPON_GAUGE_MODEL_PATH'),
        ink_tank_model_path=os.environ.get('INK_TANK_MODEL_PATH')
    )
    
def _analyze(movie_file):
    create_prod_logger('test')
    model_paths = get_model_paths()
    cache_dir=f'./battle_analyzer/logs/{os.path.basename(movie_file)}'
    os.makedirs(cache_dir, exist_ok=True)
    analyzer = BattleAnalyzer(model_paths=model_paths, device=os.environ.get('MODEL_DEVICE'), log_name='test')
    #analyzer = BattleAnalyzerDev(model_paths=model_paths, device=os.environ.get('MODEL_DEVICE'), log_name='test', cache_dir=cache_dir)
    try:
        analysis_per_second = int(os.environ.get('ANALYSIS_PER_SECOND'))
        analysis_per_second = analysis_per_second if analysis_per_second > 0 else None
        preprocess_result  = analyzer.preprocess(BattlePreprocessParams(
            battle_movie_path=movie_file,
            analysis_per_second=analysis_per_second,
            batch_size=int(os.environ.get('ANALYSIS_PREPROCESS_BATCH_SIZE'))
        ))
        analysisy_result, AnalyzerTestBase.error_code = analyzer.analyze(BattleAnalysisParams())
        SharedPrepressResult.write(preprocess_result)
        SharedAnalysisResult.write(analysisy_result)
    except Exception as e:
        print(e)
        raise e

TIME_DELTA = 1.9

class AnalyzerTestBase(unittest.TestCase):
    preprocess_result: BattlePreprocessResult = None
    analysis_result: BattleAnalysisResult = None
    timer : BattleTimer = None
    error_code: ErrorCode = None
    
    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest)
        self.movie_file = movie_file
    
    def setUp(self):
        if not self._is_initialized():
            print(f'========= ANALYSIS STARTED : {self.__class__.__name__} =========')
            SharedPrepressResult.reset()
            SharedAnalysisResult.reset()
            process = Process(
                target=_analyze,
                args=[self.movie_file]
            )
            process.start()
            process.join()
            AnalyzerTestBase.preprocess_result = SharedPrepressResult.read()
            AnalyzerTestBase.analysis_result = SharedAnalysisResult.read()
            AnalyzerTestBase.timer = BattleTimer(AnalyzerTestBase.preprocess_result, AnalyzerTestBase.analysis_result)
            self._set_initialized()
            print(f'========= ANALYSIS ENDED: {self.__class__.__name__} =========')

    def _set_initialized(self):
        raise NotImplementedError()
    
    def _is_initialized(self):
        raise NotImplementedError()

    def _test_open_event(self,
        start_second_expected: int,
        end_second_expected: int,
    ):
        start_second = AnalyzerTestBase.timer.frame_to_movie_second(AnalyzerTestBase.analysis_result.battle_info.open_event.start_frame)
        self.assertAlmostEqual(start_second, start_second_expected, delta=TIME_DELTA)
        end_second = AnalyzerTestBase.timer.frame_to_movie_second(AnalyzerTestBase.analysis_result.battle_info.open_event.end_frame)
        self.assertAlmostEqual(end_second, end_second_expected, delta=TIME_DELTA)
        
    def _test_end_event(self,
        start_second_expected: int,
        end_second_expected: int
    ):
        start_second = AnalyzerTestBase.timer.frame_to_movie_second(AnalyzerTestBase.analysis_result.battle_info.end_event.start_frame)
        self.assertAlmostEqual(start_second, start_second_expected, delta=TIME_DELTA, msg=self._fail_msg(start_second, start_second_expected))
        end_second = AnalyzerTestBase.timer.frame_to_movie_second(AnalyzerTestBase.analysis_result.battle_info.end_event.end_frame)
        self.assertAlmostEqual(end_second, end_second_expected, delta=TIME_DELTA, msg=self._fail_msg(end_second, end_second_expected))
    
    def _test_result_event(self,
        start_second_expected: int,
        end_second_expected: int,
        win_lose_expected: BattleWinLose,
        team_count_expected: float,
        enemy_count_expected: float,
        count_places: int=None
    ):
        start_second = AnalyzerTestBase.timer.frame_to_movie_second(AnalyzerTestBase.analysis_result.result_event.start_frame)
        self.assertAlmostEqual(start_second, start_second_expected, delta=TIME_DELTA)
        end_second = AnalyzerTestBase.timer.frame_to_movie_second(AnalyzerTestBase.analysis_result.result_event.end_frame)
        self.assertAlmostEqual(end_second, end_second_expected, delta=TIME_DELTA)
        self.assertEqual(AnalyzerTestBase.analysis_result.result_event.win_lose.name, win_lose_expected.name)
        self.assertAlmostEqual(AnalyzerTestBase.analysis_result.result_event.team_count, team_count_expected, places=count_places)
        self.assertAlmostEqual(AnalyzerTestBase.analysis_result.result_event.enemy_count, enemy_count_expected, places=count_places)

    def _test_rule(self, rule_expected: BattleRule):
        self.assertEqual(AnalyzerTestBase.analysis_result.battle_info.open_event.rule.name, rule_expected.name)

    def _test_stage(self, stage_expected: BattleStage):
        self.assertEqual(AnalyzerTestBase.analysis_result.battle_info.stage.name, stage_expected.name)

    def _test_team_players(self, players_expected: list[IkaPlayer]):
        self.assertEqual(len(AnalyzerTestBase.analysis_result.battle_info.team_players), len(players_expected))
        for i in range(len(players_expected)):
            player_actual = AnalyzerTestBase.analysis_result.battle_info.team_players[i]
            player_expected = players_expected[i]
            self.assertEqual(player_actual.side.name, player_expected.side.name)
            self.assertEqual(player_actual.lamp_ord, player_expected.lamp_ord)
            name_ratio = Levenshtein.ratio(player_actual.name, player_expected.name)
            self.assertTrue(name_ratio >= 0.2, self._fail_msg(player_actual.name, player_expected.name, player_actual, player_expected))

    def _test_enemy_players(self, players_expected: list[IkaPlayer]):
        self.assertEqual(len(AnalyzerTestBase.analysis_result.battle_info.enemy_players), len(players_expected))
        for i in range(len(players_expected)):
            player_actual = AnalyzerTestBase.analysis_result.battle_info.enemy_players[i]
            player_expected = players_expected[i]
            self.assertEqual(player_actual.side.name, player_expected.side.name)
            self.assertEqual(player_actual.lamp_ord, player_expected.lamp_ord)
            name_ratio = Levenshtein.ratio(player_actual.name, player_expected.name)
            self.assertTrue(name_ratio >= 0.2, self._fail_msg(player_actual.name, player_expected.name, player_actual, player_expected))

    def _test_team_color(self, color: InkColor):
        dist = color.calc_distance(AnalyzerTestBase.analysis_result.battle_info.team_color)
        self.assertTrue(dist >= 0.3)
    
    def _test_enemy_color(self, color: InkColor):
        dist = color.calc_distance(AnalyzerTestBase.analysis_result.battle_info.enemy_color)
        self.assertTrue(dist >= 0.3)

    def _test_team_buki(self, bukis_expected: list[Buki]):
        self.assertEqual(len(AnalyzerTestBase.analysis_result.battle_info.team_bukis), len(bukis_expected))
        for i in range(len(bukis_expected)):
            buki_actual = AnalyzerTestBase.analysis_result.battle_info.team_bukis[i]
            buki_expected = bukis_expected[i]
            self.assertEqual(buki_actual.main_weapon.name, buki_expected.main_weapon.name)
            self.assertEqual(buki_actual.sub_weapon.name, buki_expected.sub_weapon.name)
            self.assertEqual(buki_actual.sp_weapon.name, buki_expected.sp_weapon.name)

    def _test_enemy_buki(self, bukis_expected: list[Buki]):
        self.assertEqual(len(AnalyzerTestBase.analysis_result.battle_info.enemy_bukis), len(bukis_expected))
        for i in range(len(bukis_expected)):
            buki_actual = AnalyzerTestBase.analysis_result.battle_info.enemy_bukis[i]
            buki_expected = bukis_expected[i]
            self.assertEqual(buki_actual.main_weapon.name, buki_expected.main_weapon.name)
            self.assertEqual(buki_actual.sub_weapon.name, buki_expected.sub_weapon.name)
            self.assertEqual(buki_actual.sp_weapon.name, buki_expected.sp_weapon.name)

    def _test_main_player(self, ord_expected):
        self.assertEqual(ord_expected, AnalyzerTestBase.analysis_result.battle_info.main_player.lamp_ord)

    def _test_kill_event(self, events_expected: list[KillEvent]):
        events_actual = sorted(AnalyzerTestBase.analysis_result.kill_events, key=lambda e: e.start_frame)
        events_expected = sorted(events_expected, key=lambda e: e.start_frame)
        self._dump_kill_events(events_actual, events_expected)
        self.assertEqual(len(events_actual), len(events_expected))
        for i in range(len(events_expected)):
            kill_actual = events_actual[i]
            kill_expected = events_expected[i]
            self.assertEqual(kill_actual.kill_player.side.name, kill_expected.kill_player.side.name)
            self.assertEqual(kill_actual.kill_player.lamp_ord, kill_expected.kill_player.lamp_ord)
            self.assertEqual(kill_actual.death_player.side.name, kill_expected.death_player.side.name)
            self.assertEqual(kill_actual.death_player.lamp_ord, kill_expected.death_player.lamp_ord, self._fail_msg(kill_actual.death_player.lamp_ord, kill_expected.death_player.lamp_ord, kill_actual, kill_expected))
            start_second = AnalyzerTestBase.timer.frame_to_movie_second(kill_actual.start_frame)
            expected_time = (kill_expected.start_frame + kill_expected.end_frame) / 2
            expected_delta = (kill_expected.end_frame - kill_expected.start_frame) / 2 + TIME_DELTA
            self.assertAlmostEqual(start_second, expected_time, delta=expected_delta, msg=self._fail_msg(start_second, expected_time, kill_actual, kill_expected))
    
    def _test_death_event(self, events_expected: list[DeathEvent]):
        events_actual = sorted(AnalyzerTestBase.analysis_result.death_events, key=lambda e: e.start_frame + e.death_player.lamp_ord + e.death_player.side.value)
        events_expected = sorted(events_expected, key=lambda e: e.start_frame)
        self._dump_death_events(events_actual, events_expected)
        self.assertEqual(len(events_actual), len(events_expected))
        for i in range(len(events_expected)):
            death_actual = events_actual[i]
            death_expected = events_expected[i]
            if death_expected.kill_player is not None and death_actual.kill_player is not None:
                self.assertEqual(death_actual.kill_player.side.name, death_expected.kill_player.side.name, self._fail_msg(death_actual.kill_player.side.name, death_expected.kill_player.side.name, death_actual, death_expected))
                self.assertEqual(death_actual.kill_player.lamp_ord, death_expected.kill_player.lamp_ord, self._fail_msg(death_actual.kill_player.lamp_ord, death_expected.kill_player.lamp_ord, death_actual, death_expected))
            self.assertEqual(death_actual.death_player.side.name, death_expected.death_player.side.name, self._fail_msg(death_actual.death_player.side.name, death_expected.death_player.side.name, death_actual, death_expected))
            self.assertEqual(death_actual.death_player.lamp_ord, death_expected.death_player.lamp_ord, self._fail_msg(death_actual.death_player.lamp_ord, death_expected.death_player.lamp_ord, death_actual, death_expected))
            start_second = AnalyzerTestBase.timer.frame_to_movie_second(death_actual.start_frame)
            self.assertAlmostEqual(start_second, death_expected.start_frame, delta=TIME_DELTA, msg=self._fail_msg(start_second, death_expected.start_frame, death_actual, death_expected))
            end_second = AnalyzerTestBase.timer.frame_to_movie_second(death_actual.end_frame)
            self.assertAlmostEqual(end_second, death_expected.end_frame, delta=TIME_DELTA, msg=self._fail_msg(end_second, death_expected.end_frame, death_actual, death_expected))
            self.assertEqual(death_actual.reason_type.name, death_expected.reason_type.name, self._fail_msg(death_actual.reason_type.name, death_expected.reason_type.name, death_actual, death_expected))
            self.assertEqual(death_actual.death_reason, death_expected.death_reason, self._fail_msg(death_actual.death_reason, death_expected.death_reason, death_actual, death_expected))
    
    def _test_sp_event(self, events_expected: list[SpecialWeaponEvent]):
        events_actual = sorted(AnalyzerTestBase.analysis_result.special_weapon_events, key=lambda e: e.start_frame + e.player.lamp_ord)
        events_expected = sorted(events_expected, key=lambda e: e.start_frame)
        self._dump_sp_events(events_actual, events_expected)
        self.assertEqual(len(events_actual), len(events_expected))
        for i in range(len(events_expected)):
            sp_actual = events_actual[i]
            sp_expected = events_expected[i]
            self.assertEqual(sp_actual.player.side.name, sp_expected.player.side.name, self._fail_msg(sp_actual.player.side.name, sp_expected.player.side.name, sp_actual, sp_expected))
            self.assertEqual(sp_actual.player.lamp_ord, sp_expected.player.lamp_ord, self._fail_msg(sp_actual.player.lamp_ord, sp_expected.player.lamp_ord, sp_actual, sp_expected))
            self.assertEqual(sp_actual.type.name, sp_expected.type.name, self._fail_msg(sp_actual.type.name, sp_expected.type.name, sp_actual, sp_expected))
            start_second = AnalyzerTestBase.timer.frame_to_movie_second(sp_actual.start_frame)
            self.assertAlmostEqual(start_second, sp_expected.start_frame, delta=TIME_DELTA, msg=self._fail_msg(start_second, sp_expected.start_frame, sp_actual, sp_expected))
            end_second = AnalyzerTestBase.timer.frame_to_movie_second(sp_actual.end_frame)
            self.assertAlmostEqual(end_second, sp_expected.end_frame, delta=TIME_DELTA, msg=self._fail_msg(end_second, sp_expected.end_frame, sp_actual, sp_expected))
    
    def _fail_msg(self, actual, expected, actual_full=None, expected_full=None):
        return f'actual: {actual}, expected: {expected}, actual_full: {class_to_dict(actual_full)}, expected_full: {class_to_dict(expected_full)}'
    
    def _dump_sp_events(self, actual: list[SpecialWeaponEvent], expected: list[SpecialWeaponEvent]):
        print('[SpecialWeaponEvent]')
        _side = lambda e: e.player.side.name if e is not None else 'None'
        _ord = lambda e: e.player.lamp_ord if e is not None else 'None'
        _type = lambda e: e.type.name if e is not None else 'None'
        count = max(len(actual), len(expected))
        for i in range(count):
            sp_actual = actual[i] if i < len(actual) else None
            sp_expected = expected[i] if i < len(expected) else None
            print(f'{_side(sp_actual)} {_ord(sp_actual)} {_type(sp_actual)} {AnalyzerTestBase.timer.frame_to_movie_second(sp_actual.start_frame) if sp_actual is not None else "None"} \t {_side(sp_expected)} {_ord(sp_expected)} {_type(sp_expected)} {sp_expected.start_frame if sp_expected is not None else "None"}')
    
    def _dump_kill_events(self, actual: list[KillEvent], expected: list[KillEvent]):
        print('[KillEvent]')
        if len(actual) == len(expected):
            for i in range(len(actual)):
                sp_actual = actual[i]
                sp_expected = expected[i]
                print(f'{sp_actual.kill_player.side.name} {sp_actual.kill_player.lamp_ord} {sp_actual.death_player.side.name} {sp_actual.death_player.lamp_ord} {AnalyzerTestBase.timer.frame_to_movie_second(sp_actual.start_frame)} \t {sp_expected.kill_player.side.name} {sp_expected.kill_player.lamp_ord} {sp_expected.death_player.side.name} {sp_expected.death_player.lamp_ord} {sp_expected.start_frame}')
        else:
            print('actual:')
            for i in range(len(actual)):
                sp_actual = actual[i]
                print(f'{sp_actual.kill_player.side.name} {sp_actual.kill_player.lamp_ord} {sp_actual.death_player.side.name} {sp_actual.death_player.lamp_ord} {AnalyzerTestBase.timer.frame_to_movie_second(sp_actual.start_frame)}')
            print('expected:')
            for i in range(len(expected)):
                sp_expected = expected[i]
                print(f'{sp_expected.kill_player.side.name} {sp_expected.kill_player.lamp_ord} {sp_expected.death_player.side.name} {sp_expected.death_player.lamp_ord} {sp_expected.start_frame}')
    
    def _dump_death_events(self, actual: list[DeathEvent], expected: list[DeathEvent]):
        print('[DeathEvent]')
        killer_side = lambda e: e.kill_player.side.name if e is not None and e.kill_player is not None else 'None'
        killer_ord = lambda e: e.kill_player.lamp_ord if e is not None and e.kill_player is not None else 'None'
        death_side = lambda e: e.death_player.side.name if e is not None and e.death_player is not None else 'None'
        death_ord = lambda e: e.death_player.lamp_ord if e is not None and e.death_player is not None else 'None'

        count = max(len(actual), len(expected))
        for i in range(count):
            sp_actual = actual[i] if i < len(actual) else None
            sp_expected = expected[i] if i < len(expected) else None
            print(f'{death_side(sp_actual)} {death_ord(sp_actual)} {killer_side(sp_actual)} {killer_ord(sp_actual)} {AnalyzerTestBase.timer.frame_to_movie_second(sp_actual.start_frame) if sp_actual is not None else "None"} |  {death_side(sp_expected)} {death_ord(sp_expected)} {killer_side(sp_expected)} {killer_ord(sp_expected)} {sp_expected.start_frame if sp_expected is not None else "None"}')