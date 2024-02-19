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

class TestBattleStageTakaashi(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='まおういか', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='カービィがすきなひと', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='ゆゆまる', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='ぺんしる', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='たおしたらほんき', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='ブラボー', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='ひーとん', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='wwwwwwwwww', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleStageTakaashi.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageTakaashi.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=206,
            end_second_expected=209
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=214,
            end_second_expected=217,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=100,
            enemy_count_expected=0,
            count_places=0
        )

    def test_rule(self):
        self._test_rule(BattleRule.YAGURA)

    def test_stage(self):
        self._test_stage(BattleStage.TAKAASHI)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((82, 106, 206)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((197, 208, 110)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.R_BLASTER_ELITE_DECO, sub_weapon=SubWeapon.LINE_MARKER, sp_weapon=SpecialWeapon.MEGAPHONE_LASER_51CH),
            Buki(main_weapon=MainWeapon.NOVA_BLASTER_NEO, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.ULTRA_HANKO),
            Buki(main_weapon=MainWeapon.HOT_BLASTER_CUSTOM, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
            Buki(main_weapon=MainWeapon.CRASH_BLASTER_NEO, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.DECOY_TIRASHI),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.NOVA_BLASTER_NEO, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.ULTRA_HANKO),
            Buki(main_weapon=MainWeapon.HOT_BLASTER, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.GREAT_BARRIER),
            Buki(main_weapon=MainWeapon.HOT_BLASTER_CUSTOM, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
            Buki(main_weapon=MainWeapon.R_BLASTER_ELITE_DECO, sub_weapon=SubWeapon.LINE_MARKER, sp_weapon=SpecialWeapon.MEGAPHONE_LASER_51CH),
        ])

    def test_main_player(self):
        self._test_main_player(0)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(start_frame=35, end_frame=40, death_player=self.enemy_3, kill_player=self.team_0),
            KillEvent(start_frame=149, end_frame=154, death_player=self.enemy_1, kill_player=self.team_0),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(start_frame=54, end_frame=62, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.R_BLASTER_ELITE_DECO)),
            DeathEvent(start_frame=73 , end_frame=80, death_player=self.team_0, kill_player=self.enemy_2, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.HOT_BLASTER_CUSTOM)),
            DeathEvent(start_frame=121, end_frame=129, death_player=self.team_0, kill_player=self.enemy_3, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.R_BLASTER_ELITE_DECO)),
            DeathEvent(start_frame=160, end_frame=167, death_player=self.team_0, kill_player=self.enemy_2, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.HOT_BLASTER_CUSTOM)),
            DeathEvent(start_frame=36, end_frame=44, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=81, end_frame=88, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=60, end_frame=68, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=73, end_frame=81, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=120, end_frame=127, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=54, end_frame=62, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=74.2, end_frame=82, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=122.1, end_frame=130, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=38, end_frame=46, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=110, end_frame=118, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=179, end_frame=185, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=197, end_frame=203, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=27, end_frame=36, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=40, end_frame=49, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=76, end_frame=86, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=103, end_frame=112, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=149, end_frame=158, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=176, end_frame=185, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=29, end_frame=37, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=52, end_frame=59, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=74.1, end_frame=82, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=101, end_frame=109, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=141, end_frame=148, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=163, end_frame=171, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=183, end_frame=190, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=199, end_frame=206, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=35, end_frame=43, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=74.0, end_frame=82, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=98, end_frame=105, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=122.0, end_frame=130, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=157, end_frame=166, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=173, end_frame=180, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=189, end_frame=196, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=205, end_frame=205, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=44, end_frame=44, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=45, end_frame=45, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=104, end_frame=104, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=121, end_frame=121, type=SpecialWeaponEventType.SPOILED, player=self.team_0),
            SpecialWeaponEvent(start_frame=149.1, end_frame=149.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=151, end_frame=151, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=190, end_frame=190, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=193, end_frame=193, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=72, end_frame=72, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=75, end_frame=75, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=121, end_frame=121, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=127, end_frame=127, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=179, end_frame=179, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=196, end_frame=196, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=48.1, end_frame=48.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=59, end_frame=59, type=SpecialWeaponEventType.SPOILED, player=self.team_2),
            SpecialWeaponEvent(start_frame=106, end_frame=106, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=120, end_frame=120, type=SpecialWeaponEventType.SPOILED, player=self.team_2),
            SpecialWeaponEvent(start_frame=156, end_frame=156, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=160, end_frame=160, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=189, end_frame=189, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=191, end_frame=191, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=48.0, end_frame=48.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=48.2, end_frame=48.2, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=107.0, end_frame=107.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=107.1, end_frame=107.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=168, end_frame=168, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=169, end_frame=169, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=63, end_frame=63, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=71, end_frame=71, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=143, end_frame=143, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=148, end_frame=148, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=142, end_frame=142, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=149.0, end_frame=149.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=133, end_frame=133, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=134, end_frame=134, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=59, end_frame=59, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=62, end_frame=62, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=152, end_frame=152, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=156, end_frame=156, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['takaashi']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageTakaashi(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)