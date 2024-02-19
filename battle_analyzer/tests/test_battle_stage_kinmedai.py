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
from battle_analyzer import init

class TestBattleStageKinmedai(AnalyzerTestBase):
    initialized = False
    
    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='しかちゃん', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='いかるが', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='おこらないで', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='すいぽてのあね', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='ためねぎマン', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='よしゆき', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='あのときのイカ', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='タコのめのヒヨーク', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleStageKinmedai.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageKinmedai.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=6
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=196,
            end_second_expected=200
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=205,
            end_second_expected=209,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=47.1,
            enemy_count_expected=44.5,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.KINMEDAI)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((83, 207, 168)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((93, 143, 199)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.BUCKET_SLOSHER, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.EXAMINER, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.ENERGY_STAND),
            Buki(main_weapon=MainWeapon.SPY_GADGET, sub_weapon=SubWeapon.TRAP, sp_weapon=SpecialWeapon.SAME_RIDE),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.PABLO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.MEGAPHONE_LASER_51CH),
            Buki(main_weapon=MainWeapon.PROMODELER_MG, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.SAME_RIDE),
            Buki(main_weapon=MainWeapon.DUAL_SWEEPER_CUSTOM, sub_weapon=SubWeapon.JUMP_BEACON, sp_weapon=SpecialWeapon.DECOY_TIRASHI),
            Buki(main_weapon=MainWeapon.HISSEN_NOUVEAU, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.ENERGY_STAND),
        ])

    def test_main_player(self):
        self._test_main_player(1)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(kill_player=self.team_1, death_player=self.enemy_0, start_frame=118, end_frame=124),
            KillEvent(kill_player=self.team_1, death_player=self.enemy_1, start_frame=137, end_frame=142),
            KillEvent(kill_player=self.team_1, death_player=self.enemy_3, start_frame=165, end_frame=170)
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=75, end_frame=83, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=116, end_frame=124, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=131, end_frame=138, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=172, end_frame=181, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_3, start_frame=65, end_frame=73, reason_type=DeathReasonType.MAIN_WEAPON, death_reason='hissen_nouveau'),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_0, start_frame=119.1, end_frame=127, reason_type=DeathReasonType.SUB_WEAPON, death_reason='splash_bomb'),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_2, start_frame=175, end_frame=183, reason_type=DeathReasonType.MAIN_WEAPON, death_reason='dual_sweeper_custom'),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=66, end_frame=74, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=137.1, end_frame=141, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=192, end_frame=195, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=61, end_frame=70, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=122, end_frame=130, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=182, end_frame=190, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=42, end_frame=49, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=119.0, end_frame=127, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=177, end_frame=184, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=64, end_frame=72, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=137.0, end_frame=145, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=181, end_frame=188, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=90, end_frame=93, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=132, end_frame=141, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=185, end_frame=192, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=42, end_frame=50, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=103, end_frame=110, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=152, end_frame=157, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=165, end_frame=175, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=196, end_frame=196, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=35, end_frame=35),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=38, end_frame=38),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=65.1, end_frame=65.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=67, end_frame=67),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=166, end_frame=166),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=168, end_frame=168),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=44, end_frame=44),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.team_1, start_frame=65.0, end_frame=65.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=94, end_frame=94),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=98, end_frame=98),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=159, end_frame=159),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=173, end_frame=173),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=40.1, end_frame=40.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=42.1, end_frame=42.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=126, end_frame=126),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=127, end_frame=127),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=185, end_frame=185),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=186, end_frame=186),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=38, end_frame=38),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=40.0, end_frame=40.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=101, end_frame=101),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=114, end_frame=114),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=159, end_frame=159),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=163, end_frame=163),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=40.0, end_frame=40.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_0, start_frame=42.0, end_frame=42.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=69, end_frame=69),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=70, end_frame=70),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=109, end_frame=109),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=112, end_frame=112),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=168, end_frame=168),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=169, end_frame=169),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=27, end_frame=27),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=32, end_frame=32),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=58, end_frame=58),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=60, end_frame=60),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=106, end_frame=106),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=107, end_frame=107),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=171, end_frame=171),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=174, end_frame=174),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=51, end_frame=51),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=68, end_frame=68),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=170, end_frame=170),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=171, end_frame=171),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=35, end_frame=35),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_3, start_frame=42.2, end_frame=42.2),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=67, end_frame=67),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=80, end_frame=80),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=149.0, end_frame=149.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=149.1, end_frame=149.1),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['kinmedai']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageKinmedai(method, movie_file=movie_file))

if __name__ == "__main__":
    init()
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)