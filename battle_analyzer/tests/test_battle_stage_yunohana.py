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

class TestBattleStageYunohana(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='3れんぱいでボルネオ', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='いかるが', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='か', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='ツナマロ', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='かにかまTMLv7', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='かなすけどん', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='ブラックぶたさん03', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='ワダまる', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')

    def _set_initialized(self):
        TestBattleStageYunohana.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageYunohana.initialized
    
    def test_open_event(self):
        self._test_open_event(
            start_second_expected=1,
            end_second_expected=4
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=195,
            end_second_expected=202
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=207,
            end_second_expected=210,
            win_lose_expected=BattleWinLose.LOSE,
            team_count_expected=36.9,
            enemy_count_expected=59.7,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.YUNOHANA)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((88, 204, 178)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((108, 70, 173)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.JET_SWEEPER_CUSTOM, sub_weapon=SubWeapon.POISON_MIST, sp_weapon=SpecialWeapon.AMEFURASHI),
            Buki(main_weapon=MainWeapon.BUCKET_SLOSHER, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.ULTRA_SHOOT),
            Buki(main_weapon=MainWeapon.MOMIJI_SHOOTER, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.HOP_SONAR),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.SPLA_MANEUVER, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.KANI_TANK),
            Buki(main_weapon=MainWeapon.NOVA_BLASTER_NEO, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.ULTRA_HANKO),
            Buki(main_weapon=MainWeapon.LACT450, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.MULTI_MISSILE),
            Buki(main_weapon=MainWeapon.BOLD_MARKER, sub_weapon=SubWeapon.CURLING_BOMB, sp_weapon=SpecialWeapon.ULTRA_HANKO),
        ])

    def test_main_player(self):
        self._test_main_player(1)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(kill_player=self.team_1, death_player=self.enemy_1, start_frame=54, end_frame=60),
            KillEvent(kill_player=self.team_1, death_player=self.enemy_3, start_frame=107, end_frame=111),
            KillEvent(kill_player=self.team_1, death_player=self.enemy_0, start_frame=175, end_frame=180),
            KillEvent(kill_player=self.team_1, death_player=self.enemy_1, start_frame=180, end_frame=185),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=55.1, end_frame=63, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=149, end_frame=157, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=170, end_frame=180, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_2, start_frame=85, end_frame=93, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(SpecialWeapon.MULTI_MISSILE)),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_3, start_frame=105, end_frame=114, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.BOLD_MARKER)),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_1, start_frame=141, end_frame=148, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.NOVA_BLASTER_NEO)),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_0, start_frame=153, end_frame=161, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_MANEUVER)),
            DeathEvent(death_player=self.team_1, kill_player=self.enemy_3, start_frame=187, end_frame=195, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(SpecialWeapon.ULTRA_HANKO)),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=117, end_frame=126, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=152, end_frame=161, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=184, end_frame=192, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=72, end_frame=80, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=127, end_frame=135, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=148, end_frame=154, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=174, end_frame=182, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=57, end_frame=65, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=97, end_frame=104, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=175, end_frame=184, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=55.0, end_frame=63, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=88, end_frame=94 , reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=104, end_frame=110 , reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=144, end_frame=152 , reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=181, end_frame=189 , reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=101, end_frame=108 , reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=73, end_frame=82, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=106, end_frame=114, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=35, end_frame=35),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=36, end_frame=36),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=92, end_frame=92),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=93, end_frame=93),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=143, end_frame=143),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=148, end_frame=148),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=46, end_frame=46),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=57, end_frame=57),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=41.1, end_frame=41.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=56, end_frame=56),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=99, end_frame=99),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=103, end_frame=103),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=182.1, end_frame=182.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=183, end_frame=183),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=41.0, end_frame=41.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=61, end_frame=61),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=29, end_frame=29),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=29.0, end_frame=29.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=144.0, end_frame=144.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=154, end_frame=154),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=52, end_frame=52),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_1, start_frame=55, end_frame=55),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=79.1, end_frame=79.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=82, end_frame=82),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=162, end_frame=162),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=163, end_frame=163),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=30, end_frame=30),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=32, end_frame=32),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=79.0, end_frame=79.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=80, end_frame=80),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=144.1, end_frame=144.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=148, end_frame=148),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=192, end_frame=192),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=194, end_frame=194),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=29.1, end_frame=29.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=70, end_frame=70),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=139, end_frame=139),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=142, end_frame=142),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=180, end_frame=180),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=182.0, end_frame=182.0)
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['yunohana']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageYunohana(method, movie_file=movie_file))

if __name__ == "__main__":
    init()
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)