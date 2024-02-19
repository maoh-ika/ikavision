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

class TestBattleRuleNawabari(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='ミミのパンーー!?', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='to02', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='でんせつのコッペパン', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='いかるが', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='むひゆたれち!へよろ', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='1oz', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='あいり®♪よわいです', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='ちち', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleRuleNawabari.initialized = True
    
    def _is_initialized(self):
        return TestBattleRuleNawabari.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=2,
            end_second_expected=4
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=196,
            end_second_expected=198
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=205,
            end_second_expected=208,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=70.1,
            enemy_count_expected=23.0,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.KONBU)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((37, 177, 40)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((76, 161, 223)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon._52GALLON, sub_weapon=SubWeapon.SPLASH_SHIELD, sp_weapon=SpecialWeapon.MEGAPHONE_LASER_51CH),
            Buki(main_weapon=MainWeapon.SPLA_MANEUVER, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.KANI_TANK),
            Buki(main_weapon=MainWeapon.OVER_FLOSHER, sub_weapon=SubWeapon.SPRINKLER, sp_weapon=SpecialWeapon.AMEFURASHI),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.SPLA_ROLLER, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.GREAT_BARRIER),
            Buki(main_weapon=MainWeapon.OVER_FLOSHER, sub_weapon=SubWeapon.SPRINKLER, sp_weapon=SpecialWeapon.AMEFURASHI),
            Buki(main_weapon=MainWeapon.PROMODELER_MG, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.SAME_RIDE),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.ULTRA_SHOOT),
        ])

    def test_main_player(self):
        self._test_main_player(3)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(kill_player=self.team_3, death_player=self.enemy_0, start_frame=78, end_frame=83),
            KillEvent(kill_player=self.team_3, death_player=self.enemy_1, start_frame=80, end_frame=86),
            KillEvent(kill_player=self.team_3, death_player=self.enemy_2, start_frame=141, end_frame=146),
            KillEvent(kill_player=self.team_3, death_player=self.enemy_1, start_frame=152, end_frame=156),
            KillEvent(kill_player=self.team_3, death_player=self.enemy_1, start_frame=165, end_frame=166),
            KillEvent(kill_player=self.team_3, death_player=self.enemy_3, start_frame=182, end_frame=186),
            KillEvent(kill_player=self.team_3, death_player=self.enemy_2, start_frame=186, end_frame=191),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(death_player=self.team_3, kill_player=self.enemy_2, start_frame=90, end_frame=99, reason_type=DeathReasonType.MAIN_WEAPON, death_reason='promodeler_mg'),
            DeathEvent(death_player=self.team_3, kill_player=self.enemy_3, start_frame=163, end_frame=171, reason_type=DeathReasonType.MAIN_WEAPON, death_reason='spla_shooter'),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=85, end_frame=94, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=107, end_frame=115, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=138, end_frame=145, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=195, end_frame=195, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=103, end_frame=110, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=161, end_frame=171, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=78, end_frame=87, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=102, end_frame=143, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=171, end_frame=196, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=81, end_frame=88, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=151, end_frame=163, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=166, end_frame=174, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=186, end_frame=196, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=59, end_frame=67, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=111, end_frame=119, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=141, end_frame=149, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=162, end_frame=171, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=186, end_frame=194, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=45, end_frame=53, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=91, end_frame=99, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=149, end_frame=157, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=182, end_frame=190, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=29, end_frame=29),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=31, end_frame=31),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=54, end_frame=54),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=77, end_frame=77),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=137.0, end_frame=137.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.team_0, start_frame=137.1, end_frame=137.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=172, end_frame=172),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=173, end_frame=173),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=40.1, end_frame=40),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=44, end_frame=44),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=92, end_frame=92),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=97, end_frame=97),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=141.0, end_frame=141.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=144, end_frame=144),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=192, end_frame=192),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=193, end_frame=193),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=39, end_frame=39),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=40.2, end_frame=40),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=94, end_frame=94),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=95, end_frame=95),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=159, end_frame=159),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=159, end_frame=159),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=39, end_frame=39),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=40.3, end_frame=40),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=72, end_frame=72),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=73, end_frame=73),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=118, end_frame=118),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=119, end_frame=119),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=160, end_frame=160),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=161, end_frame=161),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=189, end_frame=189),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=190, end_frame=190),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=35, end_frame=35),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=43, end_frame=43),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=79, end_frame=79),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_1, start_frame=80, end_frame=80),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=105, end_frame=105),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=106, end_frame=106),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=148, end_frame=148),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_1, start_frame=151, end_frame=151),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=36, end_frame=36),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=57, end_frame=57),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=96, end_frame=96),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=101, end_frame=101),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=140, end_frame=140),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_2, start_frame=141.1, end_frame=141.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=160, end_frame=160),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_2, start_frame=162, end_frame=162),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=185, end_frame=185),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_2, start_frame=186, end_frame=186),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=40.0, end_frame=40),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_3, start_frame=45, end_frame=45),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=74, end_frame=74),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=84, end_frame=84),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=137.2, end_frame=137.2),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=144, end_frame=144)
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['rules']['nawabari']
    for method in config['test_methods']:
        suite.addTest(TestBattleRuleNawabari(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)