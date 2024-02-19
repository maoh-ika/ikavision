import unittest
from tests.analyzer_test_base import AnalyzerTestBase
from tests.config import config
from battle_analyzer import BattleAnalyzer, BattleAnalysisParams, BattlePreprocessParams, ModelPaths, BattleAnalysisResult
from models.battle import BattleRule, BattleSide, BattleStage, BattleWinLose
from models.ink_color import InkColor
from models.ika_player import IkaPlayer
from models.buki import MainWeapon, SubWeapon, SpecialWeapon, Buki
from events.kill_event import KillEvent
from events.death_event import DeathEvent, DeathReasonType
from events.special_weapon_event import SpecialWeaponEvent, SpecialWeaponEventType

class TestBattleStageNamerou(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='クロミ', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='う〜る', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='まおういか', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='ぽもどーろ', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='わらびもち', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='あきほ', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='スコープれんしゅうき', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='かみのみそしる', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleStageNamerou.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageNamerou.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=193,
            end_second_expected=199
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=205,
            end_second_expected=207,
            win_lose_expected=BattleWinLose.LOSE,
            team_count_expected=34.6,
            enemy_count_expected=54.8,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.NAMEROU)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((88, 160, 222)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((176, 40, 38)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.MOMIJI_SHOOTER, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.HOP_SONAR),
            Buki(main_weapon=MainWeapon.R_BLASTER_ELITE_DECO, sub_weapon=SubWeapon.LINE_MARKER, sp_weapon=SpecialWeapon.MEGAPHONE_LASER_51CH),
            Buki(main_weapon=MainWeapon.LACT450_DECO, sub_weapon=SubWeapon.SPLASH_SHIELD, sp_weapon=SpecialWeapon.SAME_RIDE),
            Buki(main_weapon=MainWeapon.GYM_WIPER, sub_weapon=SubWeapon.QUICK_BOMB, sp_weapon=SpecialWeapon.SYOKU_WONDER),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.LACT450_DECO, sub_weapon=SubWeapon.SPLASH_SHIELD, sp_weapon=SpecialWeapon.SAME_RIDE),
            Buki(main_weapon=MainWeapon.SPLA_MANEUVER_COLLABO, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
            Buki(main_weapon=MainWeapon._4K_SCOPE, sub_weapon=SubWeapon.TRAP, sp_weapon=SpecialWeapon.HOP_SONAR),
            Buki(main_weapon=MainWeapon.BOTTOLE_KAISER_FOIL, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.SUMINAGA_SHEET),
        ])

    def test_main_player(self):
        self._test_main_player(2)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(start_frame=109, end_frame=114, death_player=self.enemy_1, kill_player=self.team_2)
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(start_frame=56, end_frame=65, death_player=self.team_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=97, end_frame=105, death_player=self.team_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=138, end_frame=146, death_player=self.team_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=177, end_frame=186, death_player=self.team_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=25, end_frame=33, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=43, end_frame=51, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=64, end_frame=72, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=78, end_frame=86, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=92.2, end_frame=100, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=118, end_frame=123, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=143, end_frame=152, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=163, end_frame=171, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=185, end_frame=193, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=59, end_frame=66, death_player=self.team_2, kill_player=self.enemy_1, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_MANEUVER_COLLABO)),
            DeathEvent(start_frame=76, end_frame=83, death_player=self.team_2, kill_player=self.enemy_1, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_MANEUVER_COLLABO)),
            DeathEvent(start_frame=92.0, end_frame=100, death_player=self.team_2, kill_player=self.enemy_1, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_MANEUVER_COLLABO)),
            DeathEvent(start_frame=189, end_frame=193, death_player=self.team_2, kill_player=self.enemy_0, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.LACT450_DECO)),
            DeathEvent(start_frame=35.0, end_frame=43, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=68, end_frame=76, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=92.1, end_frame=101, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=105, end_frame=112, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=129, end_frame=137, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=154, end_frame=161, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=179, end_frame=187, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=123, end_frame=133, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=76, end_frame=84, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=109, end_frame=118, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=129, end_frame=137, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=163, end_frame=171, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=35.1, end_frame=44, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=27, end_frame=27, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=44, end_frame=44, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=124, end_frame=124, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=137, end_frame=137, type=SpecialWeaponEventType.SPOILED, player=self.team_0),
            SpecialWeaponEvent(start_frame=163, end_frame=163, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=164, end_frame=164, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=26, end_frame=26, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=43.0, end_frame=43.0, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=121, end_frame=121, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=145, end_frame=145, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=171.0, end_frame=171.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=186, end_frame=186, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=29, end_frame=29, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=97, end_frame=97, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=171.1, end_frame=171.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=178, end_frame=178, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=35, end_frame=35, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=43.1, end_frame=43.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=75, end_frame=75, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=76, end_frame=76, type=SpecialWeaponEventType.SPOILED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=95, end_frame=95, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=104, end_frame=104, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=84, end_frame=84, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=85, end_frame=85, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=136, end_frame=136, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=140, end_frame=140, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=32, end_frame=32, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=38, end_frame=38, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=112, end_frame=112, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=115, end_frame=115, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['namerou']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageNamerou(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)