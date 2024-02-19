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

class TestBattleStageMategai(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='まおういか', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='リュウセイ', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='アイスイーツ', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='はるてぃー', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='うさぎ＆ユメ', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='Yuu', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='R', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='でっぷりん！', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleStageMategai.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageMategai.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=193,
            end_second_expected=200
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=205,
            end_second_expected=208,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=47.4,
            enemy_count_expected=44.1,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.MATEGAI)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((205, 32, 70)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((75, 204, 218)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.L3_REELGUN, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.KANI_TANK),
            Buki(main_weapon=MainWeapon.NZAP89, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.DECOY_TIRASHI),
            Buki(main_weapon=MainWeapon.SHARP_MARKER, sub_weapon=SubWeapon.QUICK_BOMB, sp_weapon=SpecialWeapon.KANI_TANK),
            Buki(main_weapon=MainWeapon.SHARP_MARKER_NEO, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.SPLA_MANEUVER_COLLABO, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
            Buki(main_weapon=MainWeapon.NZAP89, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.DECOY_TIRASHI),
            Buki(main_weapon=MainWeapon.PROMODELER_RG, sub_weapon=SubWeapon.SPRINKLER, sp_weapon=SpecialWeapon.NICE_DAMA),
            Buki(main_weapon=MainWeapon.SHARP_MARKER_NEO, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
        ])

    def test_main_player(self):
        self._test_main_player(0)

    def test_kill_event(self):
        self._test_kill_event([
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(start_frame=35, end_frame=44, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(SpecialWeapon.TRIPLE_TORNADE)),
            DeathEvent(start_frame=144, end_frame=153, death_player=self.team_0, kill_player=self.enemy_0, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_MANEUVER_COLLABO)),
            DeathEvent(start_frame=184, end_frame=193, death_player=self.team_0, kill_player=self.enemy_1, reason_type=DeathReasonType.SUB_WEAPON, death_reason=Buki.get_buki_id(SubWeapon.ROBOT_BOMB)),
            DeathEvent(start_frame=140, end_frame=149, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=188, end_frame=193, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=131, end_frame=140, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=190, end_frame=193, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=24, end_frame=33, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=62.1, end_frame=72, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=129, end_frame=136, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=161, end_frame=171, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=62.0, end_frame=71, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=150, end_frame=159, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=176, end_frame=185, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=120, end_frame=128, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=186, end_frame=193, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=190, end_frame=193, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=27.1, end_frame=27.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=32.0, end_frame=32.0, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=67, end_frame=67, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=69, end_frame=69, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=115, end_frame=115, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=116, end_frame=116, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=178, end_frame=178, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=179.1, end_frame=179.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=29, end_frame=29, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=32.2, end_frame=32.2, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=82, end_frame=82, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=84, end_frame=84, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=173.0, end_frame=173.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=180, end_frame=180, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=35.1, end_frame=35.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=41, end_frame=41, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=91, end_frame=91, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=93, end_frame=93, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=169, end_frame=169, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=171, end_frame=171, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=122, end_frame=122, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=126, end_frame=126, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=28.0, end_frame=28.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=40, end_frame=40, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=112, end_frame=112, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=128, end_frame=128, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=28.1, end_frame=28.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=34, end_frame=34, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=101, end_frame=101, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=151, end_frame=151, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=35.0, end_frame=35.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=53, end_frame=53, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=113, end_frame=113, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=116, end_frame=116, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=173.1, end_frame=173.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=179.0, end_frame=179.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=27.0, end_frame=27.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=32.1, end_frame=32.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=85, end_frame=85, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=86, end_frame=86, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=135, end_frame=135, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=137, end_frame=137, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),

        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['mategai']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageMategai(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)