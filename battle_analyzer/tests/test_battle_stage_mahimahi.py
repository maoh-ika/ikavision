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

class TestBattleStageMahimahi(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='まおういか', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='そちん', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='すめし', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='◆わらびもち◇', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='たおしたをたおした', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='Rei Mitu', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='*とうみん*', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='まあぼおどうふ', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')

    def _set_initialized(self):
        TestBattleStageMahimahi.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageMahimahi.initialized
    
    def test_open_event(self):
        self._test_open_event(
            start_second_expected=1,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=193,
            end_second_expected=197
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=203,
            end_second_expected=206,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=48.6,
            enemy_count_expected=44.1,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.MAHIMAHI)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((68, 130, 218)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((202, 81, 75)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.DAPPLE_DUALIES_NOUVEAU, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.SAME_RIDE),
            Buki(main_weapon=MainWeapon.BOTTOLE_KAISER_FOIL, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.SUMINAGA_SHEET),
            Buki(main_weapon=MainWeapon.SHARP_MARKER_NEO, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.SHARP_MARKER, sub_weapon=SubWeapon.QUICK_BOMB, sp_weapon=SpecialWeapon.KANI_TANK),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.VINCENT_NOUVEAU, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.MULTI_MISSILE),
            Buki(main_weapon=MainWeapon.VARIABLE_ROLLER, sub_weapon=SubWeapon.TRAP, sp_weapon=SpecialWeapon.MULTI_MISSILE),
            Buki(main_weapon=MainWeapon.HOT_BLASTER_CUSTOM, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
            Buki(main_weapon=MainWeapon. NZAP89, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.DECOY_TIRASHI),
        ])

    def test_main_player(self):
        self._test_main_player(0)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(kill_player=self.team_0, death_player=self.enemy_1, start_frame=57, end_frame=62),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_2, start_frame=97, end_frame=102),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_0, start_frame=139, end_frame=144),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_1, start_frame=147, end_frame=152),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_2, start_frame=155, end_frame=160),
            KillEvent(kill_player=self.team_0, death_player=self.enemy_0, start_frame=160, end_frame=165)
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_2, start_frame=61, end_frame=69, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.HOT_BLASTER_CUSTOM)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_2, start_frame=84, end_frame=91, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.HOT_BLASTER_CUSTOM)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_1, start_frame=105, end_frame=112, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.VARIABLE_ROLLER)),
            DeathEvent(death_player=self.team_0, kill_player=self.enemy_2, start_frame=120, end_frame=127, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.HOT_BLASTER_CUSTOM)),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=36, end_frame=45, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=55, end_frame=64, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=123.1, end_frame=131, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=190, end_frame=193, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=117, end_frame=125, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=133, end_frame=140, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=92, end_frame=100, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=140, end_frame=149, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=160, end_frame=167, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=189, end_frame=193, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=57, end_frame=65, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=116, end_frame=123, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=147, end_frame=155, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=96, end_frame=104, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=155, end_frame=163, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=174, end_frame=181, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=123.0, end_frame=131, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=145, end_frame=152, reason_type=DeathReasonType.UNKNOWN, death_reason='')
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=48, end_frame=48, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=55, end_frame=55, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=151, end_frame=151, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=157, end_frame=157, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=192.0, end_frame=192.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=192.1, end_frame=192.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=54, end_frame=54, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=56, end_frame=56, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=129, end_frame=129, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=130, end_frame=130, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=119, end_frame=119, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=122, end_frame=122, type=SpecialWeaponEventType.SPOILED, player=self.team_2),
            SpecialWeaponEvent(start_frame=159, end_frame=159, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=161, end_frame=161, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=34.1, end_frame=34.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=59, end_frame=59, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=106, end_frame=106, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=107, end_frame=107, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=186, end_frame=186, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=34.0, end_frame=34.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=35.0, end_frame=35.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=30, end_frame=30, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=31, end_frame=31, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=92.0, end_frame=92.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=92.1, end_frame=92.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=171, end_frame=171, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=172, end_frame=172, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=55, end_frame=55, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=62, end_frame=62, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=121, end_frame=121, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=131, end_frame=131, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=35.1, end_frame=35.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=37, end_frame=37, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=94, end_frame=94, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=95, end_frame=95, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=176.0, end_frame=176.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=176.1, end_frame=176.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3)
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['mahimahi']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageMahimahi(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)