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

class TestBattleStageNampula(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='まおういか', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='tofu.たいむ', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='かさこじぞうさいきょ', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='ちーすけ', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='ぽー', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='よゆうのよしおくん', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='いかのおすし', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='まこと', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleStageNampula.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageNampula.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=337,
            end_second_expected=340
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=345,
            end_second_expected=348,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=75,
            enemy_count_expected=73,
            count_places=0
        )

    def test_rule(self):
        self._test_rule(BattleRule.AREA)

    def test_stage(self):
        self._test_stage(BattleStage.NAMPULA)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((189, 73, 69)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((69, 123, 215)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon._96GALLON, sub_weapon=SubWeapon.SPRINKLER, sp_weapon=SpecialWeapon.KYUUINKI),
            Buki(main_weapon=MainWeapon.KELVIN535, sub_weapon=SubWeapon.SPLASH_SHIELD, sp_weapon=SpecialWeapon.NICE_DAMA),
            Buki(main_weapon=MainWeapon.SPLA_ROLLER, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.GREAT_BARRIER),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.SPY_GADGET_SOLARE, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.SUMINAGA_SHEET),
            Buki(main_weapon=MainWeapon.WAKABA_SHOOTER, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.GREAT_BARRIER),
            Buki(main_weapon=MainWeapon.OVER_FLOSHER, sub_weapon=SubWeapon.SPRINKLER, sp_weapon=SpecialWeapon.AMEFURASHI),
            Buki(main_weapon=MainWeapon.VINCENT, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.HOP_SONAR),
        ])

    def test_main_player(self):
        self._test_main_player(0)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(start_frame=29, end_frame=34, death_player=self.enemy_3, kill_player=self.team_0),
            KillEvent(start_frame=59, end_frame=64, death_player=self.enemy_2, kill_player=self.team_0),
            KillEvent(start_frame=121, end_frame=126, death_player=self.enemy_3, kill_player=self.team_0),
            KillEvent(start_frame=148, end_frame=153, death_player=self.enemy_3, kill_player=self.team_0),
            KillEvent(start_frame=150, end_frame=155, death_player=self.enemy_1, kill_player=self.team_0),
            KillEvent(start_frame=165, end_frame=170, death_player=self.enemy_2, kill_player=self.team_0),
            KillEvent(start_frame=168, end_frame=173, death_player=self.enemy_0, kill_player=self.team_0),
            KillEvent(start_frame=173, end_frame=178, death_player=self.enemy_3, kill_player=self.team_0),
            KillEvent(start_frame=190, end_frame=195, death_player=self.enemy_3, kill_player=self.team_0),
            KillEvent(start_frame=280, end_frame=285, death_player=self.enemy_0, kill_player=self.team_0),
            KillEvent(start_frame=298, end_frame=303, death_player=self.enemy_2, kill_player=self.team_0),
            KillEvent(start_frame=313, end_frame=318, death_player=self.enemy_1, kill_player=self.team_0),
            KillEvent(start_frame=327, end_frame=332, death_player=self.enemy_2, kill_player=self.team_0),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(start_frame=91, end_frame=99 , death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(SpecialWeapon.HOP_SONAR)),
            DeathEvent(start_frame=130, end_frame=138 , death_player=self.team_0, kill_player=self.enemy_1, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.WAKABA_SHOOTER)),
            DeathEvent(start_frame=220, end_frame=227, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.VINCENT)),
            DeathEvent(start_frame=258, end_frame=265, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.VINCENT)),
            DeathEvent(start_frame=282, end_frame=289, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.VINCENT)),
            DeathEvent(start_frame=313.1, end_frame=321, death_player=self.team_0, kill_player=self.enemy_2, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.OVER_FLOSHER)),
            DeathEvent(start_frame=328, end_frame=335 , death_player=self.team_0, kill_player=self.enemy_2, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(SpecialWeapon.AMEFURASHI)),
            DeathEvent(start_frame=81, end_frame=89, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=96, end_frame=103, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=213, end_frame=222, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=226, end_frame=234, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=270 , end_frame=277, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=304, end_frame=312, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=90, end_frame=99, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=109, end_frame=117, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=150, end_frame=158, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=217, end_frame=222, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=232, end_frame=242, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=302, end_frame=311, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=321, end_frame=330, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=89, end_frame=96, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=154, end_frame=163, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=266, end_frame=273, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=308, end_frame=316, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=334.1, end_frame=337, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=28, end_frame=38, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=90, end_frame=95, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=168, end_frame=175, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=280, end_frame=287, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=334.2, end_frame=338, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=31, end_frame=39, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=137, end_frame=144, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=150, end_frame=158, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=262, end_frame=269, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=313.0, end_frame=321, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=25, end_frame=33, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=60, end_frame=68, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=165, end_frame=173, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=181, end_frame=189, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=204, end_frame=213, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=243, end_frame=251, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=270, end_frame=279, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=298, end_frame=305, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=327, end_frame=335, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=29, end_frame=37, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=54, end_frame=62, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=121, end_frame=129, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=149, end_frame=157, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=173, end_frame=181, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=191, end_frame=199, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=260, end_frame=267, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=320, end_frame=328, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=334.0, end_frame=337, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=44.2, end_frame=44.2, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=56, end_frame=56, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=109, end_frame=109, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=116.1, end_frame=116.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=159, end_frame=159, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=161, end_frame=161, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=191.0, end_frame=191.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=196, end_frame=196, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=243, end_frame=243, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=244, end_frame=244, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=305, end_frame=305, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=309, end_frame=309, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=41, end_frame=41, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=42, end_frame=42, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=115.1, end_frame=115.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=116.2, end_frame=116.2, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=148, end_frame=148, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=149, end_frame=149, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=191.1, end_frame=191.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=192, end_frame=192, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=250, end_frame=250, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=251, end_frame=251, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=323.1, end_frame=323.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=325, end_frame=325, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=41, end_frame=41, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=44.0, end_frame=44.0, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=133, end_frame=133, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=135.1, end_frame=135.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=197, end_frame=197, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=198, end_frame=198, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=271.1, end_frame=271.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=281, end_frame=281, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=44.1, end_frame=44.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=54, end_frame=54, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=103, end_frame=103, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=115.0, end_frame=115.0, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=143, end_frame=143, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=145, end_frame=145, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=213, end_frame=213, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=216, end_frame=216, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=236, end_frame=236, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=247, end_frame=247, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=327, end_frame=327, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=328, end_frame=328, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=51, end_frame=51, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=52, end_frame=52, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=82, end_frame=82, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=83, end_frame=83, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=149, end_frame=149, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=150, end_frame=150, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=193, end_frame=193, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=194, end_frame=194, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=221.0, end_frame=221.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=221.1, end_frame=221.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=270, end_frame=270, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=271.0, end_frame=271.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=319, end_frame=319, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=320, end_frame=320, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=49, end_frame=49, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=65, end_frame=65, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=96, end_frame=96, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=101, end_frame=101, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=178, end_frame=178, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=208.0, end_frame=208.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=246, end_frame=246, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=249, end_frame=249, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=296, end_frame=296, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=300, end_frame=300, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=48, end_frame=48, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=53, end_frame=53, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=89, end_frame=89, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=91, end_frame=91, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=134, end_frame=134, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=135.0, end_frame=135.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=223, end_frame=223, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=232, end_frame=232, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=322, end_frame=322, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=323.0, end_frame=323.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=80, end_frame=80, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=81, end_frame=81, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=116.0, end_frame=116.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=117, end_frame=117, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=208.1, end_frame=208.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=210, end_frame=210, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=252, end_frame=252, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=253, end_frame=253, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=296.0, end_frame=296.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=296.1, end_frame=296.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3)
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['nampula']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageNampula(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)