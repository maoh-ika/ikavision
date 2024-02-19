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

class TestBattleStageGonzui(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='まおういか', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='ココア&まっちゃ', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='nisshi', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='てんさいリッターさま', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='ぐるぐるぷりん', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='すぎやま', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='すーたろー', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='たろす', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')

    def _set_initialized(self):
        TestBattleStageGonzui.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageGonzui.initialized
    
    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=2
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=239,
            end_second_expected=242
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=248,
            end_second_expected=251,
            win_lose_expected=BattleWinLose.LOSE,
            team_count_expected=0,
            enemy_count_expected=100,
            count_places=0
        )

    def test_rule(self):
        self._test_rule(BattleRule.HOKO)

    def test_stage(self):
        self._test_stage(BattleStage.GONZUI)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((77, 159, 217)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((173, 42, 40)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.BUCKET_SLOSHER, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.ELITER_4K, sub_weapon=SubWeapon.TRAP, sp_weapon=SpecialWeapon.HOP_SONAR),
            Buki(main_weapon=MainWeapon.SCREW_SLOSHER_NEO, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.ULTRA_SHOOT),
            Buki(main_weapon=MainWeapon.ELITER_4K, sub_weapon=SubWeapon.TRAP, sp_weapon=SpecialWeapon.HOP_SONAR),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.SBLAST91, sub_weapon=SubWeapon.QUICK_BOMB, sp_weapon=SpecialWeapon.NICE_DAMA),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.DAPPLE_DUALIES_NOUVEAU, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.SAME_RIDE),
            Buki(main_weapon=MainWeapon.SPLA_MANEUVER_COLLABO, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
        ])

    def test_main_player(self):
        self._test_main_player(0)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(kill_player=self.team_0, death_player=self.enemy_3, start_frame=84, end_frame=89),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_0, start_frame=145, end_frame=150),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_3, start_frame=160, end_frame=165),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_1, start_frame=230, end_frame=235)
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_1, start_frame=61, end_frame=69, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_SHOOTER_COLLABO)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_3, start_frame=104, end_frame=111, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_MANEUVER_COLLABO)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_3, start_frame=117, end_frame=124, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(SpecialWeapon.ULTRA_TYAKUTI)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_2, start_frame=162, end_frame=169, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.DAPPLE_DUALIES_NOUVEAU)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_1, start_frame=201, end_frame=208, reason_type=DeathReasonType.SUB_WEAPON, death_reason=Buki.get_buki_id(SubWeapon.SPLASH_BOMB)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_2, start_frame=232, end_frame=239, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.DAPPLE_DUALIES_NOUVEAU)),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=43, end_frame=51, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=64, end_frame=71, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=126.0, end_frame=134, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=180.0, end_frame=188, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=199, end_frame=206, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=213, end_frame=221, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=233.0, end_frame=240, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=78, end_frame=85, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=158, end_frame=167, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=180.1, end_frame=188, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=198, end_frame=206, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=229, end_frame=237, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=194, end_frame=204, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=222, end_frame=231, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=238, end_frame=239, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=28, end_frame=36, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=52, end_frame=60, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=95, end_frame=103, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=122 , end_frame=131, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=146, end_frame=154, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=219, end_frame=228, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=42, end_frame=51, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=62, end_frame=70, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=90, end_frame=98, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=147, end_frame=186, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=231, end_frame=238, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=57, end_frame=65, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=85, end_frame=93, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=129, end_frame=137, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=177, end_frame=185, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=214, end_frame=221, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=84, end_frame=92, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=126.1, end_frame=134, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=160, end_frame=168, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=197, end_frame=204, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=233.1, end_frame=240, reason_type=DeathReasonType.UNKNOWN, death_reason='')
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=52, end_frame=52),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=53, end_frame=53),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=226, end_frame=226),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.team_0, start_frame=232, end_frame=232),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=39.1, end_frame=39.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=39.2, end_frame=39.2),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=129, end_frame=129),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=146, end_frame=146),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=67, end_frame=67),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=74, end_frame=74),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=136, end_frame=136),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=142, end_frame=142),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=86, end_frame=86),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=92, end_frame=92),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=181, end_frame=181),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=194, end_frame=194),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=39.0, end_frame=39.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_1, start_frame=42.0, end_frame=42.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=89.0, end_frame=89.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_1, start_frame=89.1, end_frame=89.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=118, end_frame=118),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=121, end_frame=121),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=192, end_frame=192),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=196, end_frame=196),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=53, end_frame=53),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_2, start_frame=57, end_frame=57),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=72, end_frame=72),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_2, start_frame=85, end_frame=85),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=108, end_frame=108),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=109, end_frame=109),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=147, end_frame=147),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=154, end_frame=154),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=196, end_frame=196),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=209, end_frame=209),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=33, end_frame=33),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=42.1, end_frame=42.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=61, end_frame=61),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=62, end_frame=62),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=105, end_frame=105),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=115, end_frame=115),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=156, end_frame=156),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=157, end_frame=157),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=191, end_frame=191),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_3, start_frame=197, end_frame=197),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=218, end_frame=218),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=219, end_frame=219),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['gonzui']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageGonzui(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)