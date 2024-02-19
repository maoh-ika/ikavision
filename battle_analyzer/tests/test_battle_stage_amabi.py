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

class TestBattleStageAmabi(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='Novaust', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='まおういか', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='↓↓↓', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='Hiohon', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='D', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='*りんまる*', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='ぴーこ', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='ダークまつだ', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')

    def _set_initialized(self):
        TestBattleStageAmabi.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageAmabi.initialized
    
    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=193,
            end_second_expected=198
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=204,
            end_second_expected=206,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=44.1,
            enemy_count_expected=44.0,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.AMABI)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((210, 41, 67)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((67, 195, 207)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.BOLD_MARKER_NEO, sub_weapon=SubWeapon.JUMP_BEACON, sp_weapon=SpecialWeapon.MEGAPHONE_LASER_51CH),
            Buki(main_weapon=MainWeapon.HOKUSAI, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.SYOKU_WONDER),
            Buki(main_weapon=MainWeapon.MOMIJI_SHOOTER, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.HOP_SONAR),
            Buki(main_weapon=MainWeapon.SPLA_MANEUVER_COLLABO, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.VINCENT_NOUVEAU, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.MULTI_MISSILE),
            Buki(main_weapon=MainWeapon.CAMPING_SHELTER_SOLARE, sub_weapon=SubWeapon.TRAP, sp_weapon=SpecialWeapon.ULTRA_SHOOT),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.MOMIJI_SHOOTER, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.HOP_SONAR),
        ])

    def test_main_player(self):
        self._test_main_player(1)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(kill_player=self.team_1, death_player=self.enemy_1, start_frame=129, end_frame=134),
            KillEvent(kill_player=self.team_1, death_player=self.enemy_0, start_frame=142, end_frame=147),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=68, end_frame=76, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=138, end_frame=146, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=165, end_frame=171, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=176.1, end_frame=182, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_1, start_frame=64, end_frame=72, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.CAMPING_SHELTER_SOLARE)),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_0, start_frame=99.0, end_frame=108, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.VINCENT_NOUVEAU)),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_1, start_frame=128.0, end_frame=136, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.CAMPING_SHELTER_SOLARE)),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_0, start_frame=159, end_frame=167, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.VINCENT_NOUVEAU)),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=191.0, end_frame=193, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=74, end_frame=83, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=132, end_frame=141, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=169, end_frame=178, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=57, end_frame=67, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=99.2, end_frame=108, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=147, end_frame=156, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=177, end_frame=185, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=35, end_frame=44, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=68, end_frame=76, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=141, end_frame=150, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=176.0, end_frame=184, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=65, end_frame=73, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=99.1, end_frame=108, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=128.1, end_frame=136, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=167, end_frame=175, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=191.1, end_frame=193, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=76, end_frame=85, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=110, end_frame=118, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=132, end_frame=141, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=188, end_frame=193, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=84, end_frame=93, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=27, end_frame=27, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=31, end_frame=31, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=66, end_frame=66, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=68, end_frame=68, type=SpecialWeaponEventType.SPOILED, player=self.team_0),
            SpecialWeaponEvent(start_frame=86, end_frame=86, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=98, end_frame=98, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=127, end_frame=127, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=128, end_frame=128, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=31.0, end_frame=31.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=65, end_frame=65, type=SpecialWeaponEventType.SPOILED, player=self.team_1),
            SpecialWeaponEvent(start_frame=95, end_frame=95, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=97, end_frame=97, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=150, end_frame=150, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=156, end_frame=156, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=185, end_frame=185, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=186, end_frame=186, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=43, end_frame=43, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=50, end_frame=50, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=110, end_frame=110, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=118, end_frame=118, type=SpecialWeaponEventType.TRIGGERED, player=self.team_2),
            SpecialWeaponEvent(start_frame=169.0, end_frame=169.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=169.1, end_frame=169.1, type=SpecialWeaponEventType.SPOILED, player=self.team_2),
            SpecialWeaponEvent(start_frame=193, end_frame=193, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2),
            SpecialWeaponEvent(start_frame=31.1, end_frame=31.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=51, end_frame=51, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=124, end_frame=124, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=132, end_frame=132, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=24, end_frame=24, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=25, end_frame=25, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=85.0, end_frame=85.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=85.1, end_frame=85.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=125, end_frame=125, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=126, end_frame=126, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=170, end_frame=170, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=177, end_frame=177, type=SpecialWeaponEventType.SPOILED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=190, end_frame=190, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=191, end_frame=191, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=86, end_frame=86, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=100, end_frame=100, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=161, end_frame=161, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=162, end_frame=162, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=34, end_frame=34, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=36, end_frame=36, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=76, end_frame=76, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=77, end_frame=77, type=SpecialWeaponEventType.SPOILED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=102.0, end_frame=102.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=102.1, end_frame=102.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=164, end_frame=164, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=165, end_frame=165, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=31.2, end_frame=31.2, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=40, end_frame=40, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=70, end_frame=70, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=79, end_frame=79, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=141, end_frame=141, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=143, end_frame=143, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['amabi']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageAmabi(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)