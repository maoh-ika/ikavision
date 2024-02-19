import unittest
from tests.analyzer_test_base import AnalyzerTestBase
from tests.config import config
from models.battle import BattleRule, BattleSide, BattleStage, BattleWinLose
from models.ink_color import InkColor
from models.ika_player import IkaPlayer
from models.buki import MainWeapon, SubWeapon, SpecialWeapon, Buki
from events.kill_event import KillEvent
from events.death_event import DeathEvent, DeathReasonType
from events.special_weapon_event import SpecialWeaponEvent, SpecialWeaponEventType

class TestBattleRuleHokoCount(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='まおういか', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='こんぺいとう', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name="イチゴ⇒('O`)", lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='あーもんど02_AD', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='みみみ', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='あこ', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='vcomftいえ^3', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='シュークリーメ', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleRuleHokoCount.initialized = True
    
    def _is_initialized(self):
        return TestBattleRuleHokoCount.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=4
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=328,
            end_second_expected=332
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=338,
            end_second_expected=341,
            win_lose_expected=BattleWinLose.LOSE,
            team_count_expected=39,
            enemy_count_expected=95,
            count_places=0 
        )

    def test_rule(self):
        self._test_rule(BattleRule.HOKO)

    def test_stage(self):
        self._test_stage(BattleStage.HIRAME)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((71, 100, 203)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((174, 197, 94)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.HOKUSAI, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.SYOKU_WONDER),
            Buki(main_weapon=MainWeapon.CLASSIC_SQUIFFER, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.GREAT_BARRIER),
            Buki(main_weapon=MainWeapon.KELVIN535, sub_weapon=SubWeapon.SPLASH_SHIELD, sp_weapon=SpecialWeapon.NICE_DAMA),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.MOMIJI_SHOOTER, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.HOP_SONAR),
            Buki(main_weapon=MainWeapon.EXPLOSHER, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.AMEFURASHI),
            Buki(main_weapon=MainWeapon.CARBON_ROLLER_DECO, sub_weapon=SubWeapon.QUICK_BOMB, sp_weapon=SpecialWeapon.ULTRA_SHOOT),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
        ])

    def test_main_player(self):
        self._test_main_player(0)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(start_frame=170, end_frame=175, kill_player=self.team_0, death_player=self.enemy_0),
            KillEvent(start_frame=233, end_frame=238, kill_player=self.team_0, death_player=self.enemy_0),
            KillEvent(start_frame=310, end_frame=315, kill_player=self.team_0, death_player=self.enemy_0),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(start_frame=60, end_frame=68, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_SHOOTER_COLLABO)),
            DeathEvent(start_frame=74, end_frame=81, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_SHOOTER_COLLABO)),
            DeathEvent(start_frame=93, end_frame=98, death_player=self.team_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=188, end_frame=195, death_player=self.team_0, kill_player=self.enemy_0, reason_type=DeathReasonType.SUB_WEAPON, death_reason=Buki.get_buki_id(SubWeapon.TORPEDE)),
            DeathEvent(start_frame=220, end_frame=227, death_player=self.team_0, kill_player=self.enemy_2, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.CARBON_ROLLER_DECO)),
            DeathEvent(start_frame=234 , end_frame=242, death_player=self.team_0, kill_player=self.enemy_2, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(SpecialWeapon.ULTRA_SHOOT)),
            DeathEvent(start_frame=283, end_frame=290, death_player=self.team_0, kill_player=self.enemy_0, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.MOMIJI_SHOOTER)),
            DeathEvent(start_frame=30, end_frame=38, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=53, end_frame=60, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=67, end_frame=73, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=144, end_frame=152, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=195, end_frame=198, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=202, end_frame=209, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=250, end_frame=258, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=300, end_frame=308, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=312, end_frame=320, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=46, end_frame=55, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=66, end_frame=74, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=81, end_frame=90, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=122, end_frame=131, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=149, end_frame=158, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=199, end_frame=208, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=224, end_frame=234, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=279, end_frame=288, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=312, end_frame=321, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=327, end_frame=328, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=44, end_frame=52, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=59, end_frame=64, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=73, end_frame=80, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=110, end_frame=116, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=136, end_frame=141, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=165, end_frame=173, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=196, end_frame=201, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=229, end_frame=235, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=241, end_frame=246, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=282, end_frame=287, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=296.1, end_frame=302, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=318 , end_frame=326, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=29, end_frame=36, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=170, end_frame=177, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=233, end_frame=241, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=310 , end_frame=318, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=166, end_frame=173, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=314, end_frame=321, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=79, end_frame=86, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=98, end_frame=105, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=138, end_frame=145, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=172, end_frame=180, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=272, end_frame=280, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=300, end_frame=308, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=75, end_frame=83, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=127, end_frame=135, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=159, end_frame=167, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=230, end_frame=238, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=296.0, end_frame=304, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=318, end_frame=326, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=49.1, end_frame=49.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=53, end_frame=53, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=110, end_frame=110, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=113, end_frame=113, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=142, end_frame=142 , type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=152, end_frame=152, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=212, end_frame=212, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=213.1, end_frame=213.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=261.1, end_frame=261.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=262.2, end_frame=262.2, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=307, end_frame=307, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=312, end_frame=312, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=87, end_frame=87, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=144, end_frame=144, type=SpecialWeaponEventType.SPOILED, player=self.team_1),
            SpecialWeaponEvent(start_frame=167, end_frame=167, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=194, end_frame=194, type=SpecialWeaponEventType.SPOILED, player=self.team_1),
            SpecialWeaponEvent(start_frame=240, end_frame=240, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=250, end_frame=250, type=SpecialWeaponEventType.SPOILED, player=self.team_1),
            SpecialWeaponEvent(start_frame=272.1, end_frame=272.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=300, end_frame=300, type=SpecialWeaponEventType.SPOILED, player=self.team_1),
            SpecialWeaponEvent(start_frame=116, end_frame=116, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=117, end_frame=117, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=265, end_frame=265, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=272.0, end_frame=272.0, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=58.0, end_frame=58.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=58.1, end_frame=58.1, type=SpecialWeaponEventType.SPOILED, player=self.team_3),
            SpecialWeaponEvent(start_frame=71, end_frame=71, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=72, end_frame=72, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=87, end_frame=87, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=90, end_frame=90, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=134, end_frame=134, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=136, end_frame=136, type=SpecialWeaponEventType.SPOILED, player=self.team_3),
            SpecialWeaponEvent(start_frame=153, end_frame=153, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=154, end_frame=154, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=218, end_frame=218, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=229, end_frame=229, type=SpecialWeaponEventType.SPOILED, player=self.team_3),
            SpecialWeaponEvent(start_frame=261.0, end_frame=261.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=262.0, end_frame=262.0, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=317.0, end_frame=317.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=317.1, end_frame=317.1, type=SpecialWeaponEventType.SPOILED, player=self.team_3),
            SpecialWeaponEvent(start_frame=65, end_frame=65, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=66, end_frame=66, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=98.1, end_frame=98.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=99, end_frame=99, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=142, end_frame=142, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=143, end_frame=143, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=213.0, end_frame=213.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=221, end_frame=221, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=296.1, end_frame=296.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=296.2, end_frame=296.2, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=38.0, end_frame=38.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=38.1, end_frame=38.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=94, end_frame=94, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=98.0, end_frame=98.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=148, end_frame=148, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=149, end_frame=149, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=202, end_frame=202, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=203, end_frame=203, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=261.2, end_frame=261.2, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=262.1, end_frame=262.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=65, end_frame=65, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=68, end_frame=68, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=227, end_frame=227, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=230.1, end_frame=230.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=49.0, end_frame=49.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=54, end_frame=54, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=204, end_frame=204, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=230.0, end_frame=230.0, type=SpecialWeaponEventType.SPOILED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=282, end_frame=282, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=296.0, end_frame=296.0, type=SpecialWeaponEventType.SPOILED, player=self.enemy_3),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['rules']['hoko']['count']
    for method in config['test_methods']:
        suite.addTest(TestBattleRuleHokoCount(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)