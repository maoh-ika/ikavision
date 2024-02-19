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

class TestBattleStageKusaya(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='きなこもち', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='スプラだけはは', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='いかるが', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='とびうお', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='chip', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='なる', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='とーと', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='ひつき', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleStageKusaya.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageKusaya.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=1,
            end_second_expected=7
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=198,
            end_second_expected=207
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=211,
            end_second_expected=215,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=60.6,
            enemy_count_expected=35.0,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.KUSAYA)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((78, 202, 174)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((117, 152, 203)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.PROMODELER_RG, sub_weapon=SubWeapon.SPRINKLER, sp_weapon=SpecialWeapon.NICE_DAMA),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.ULTRA_SHOOT),
            Buki(main_weapon=MainWeapon.BUCKET_SLOSHER, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.HISSEN_NOUVEAU, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.ENERGY_STAND),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon.PROMODELER_RG, sub_weapon=SubWeapon.SPRINKLER, sp_weapon=SpecialWeapon.NICE_DAMA),
            Buki(main_weapon=MainWeapon.NZAP89, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.DECOY_TIRASHI),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.PROMODELER_MG, sub_weapon=SubWeapon.TANSAN_BOMB, sp_weapon=SpecialWeapon.SAME_RIDE),
        ])

    def test_main_player(self):
        self._test_main_player(2)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(kill_player=self.team_2, death_player=self.enemy_0, start_frame=52, end_frame=57),
            KillEvent(kill_player=self.team_2, death_player=self.enemy_1, start_frame=65, end_frame=71),
            KillEvent(kill_player=self.team_2, death_player=self.enemy_2, start_frame=195, end_frame=198),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(death_player=self.team_0, kill_player=None, start_frame=46, end_frame=54, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=86, end_frame=93, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=134, end_frame=141, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_1, kill_player=None, start_frame=158, end_frame=166, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=122, end_frame=130, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=None, start_frame=181, end_frame=189, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_2, kill_player=self.enemy_2, start_frame=195.1, end_frame=198, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.SPLA_SHOOTER_COLLABO)),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=45, end_frame=50, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=82.1, end_frame=89.2, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.team_3, kill_player=None, start_frame=102.1, end_frame=110.0, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=50, end_frame=59, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=82.3, end_frame=89.0, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=102.2, end_frame=110.1, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=136, end_frame=143, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=157, end_frame=164, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_0, kill_player=None, start_frame=189.0, end_frame=197, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=66, end_frame=74, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=82.0, end_frame=89.1, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=102.0, end_frame=109, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=138, end_frame=146, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_1, kill_player=None, start_frame=180, end_frame=189, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=150, end_frame=158, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=175, end_frame=188, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_2, kill_player=None, start_frame=195.0, end_frame=198, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=35, end_frame=44, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=70, end_frame=77, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=124, end_frame=131, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=144, end_frame=152, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=169, end_frame=177, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(death_player=self.enemy_3, kill_player=None, start_frame=189.1, end_frame=192, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=29, end_frame=29),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=30, end_frame=30),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=67, end_frame=67),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=68, end_frame=68),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=97.1, end_frame=97.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=98, end_frame=98),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=117.1, end_frame=117.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=119.0, end_frame=119.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=138, end_frame=138),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=142, end_frame=142),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=170, end_frame=170),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=171.1, end_frame=171.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0, start_frame=194, end_frame=194),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_0, start_frame=195, end_frame=195),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=41.1, end_frame=41.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_1, start_frame=50, end_frame=50),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1, start_frame=132, end_frame=132),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.team_1, start_frame=133.1, end_frame=133.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=51, end_frame=51),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=53, end_frame=53),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=85, end_frame=85),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=90, end_frame=90),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_2, start_frame=159, end_frame=159),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_2, start_frame=160, end_frame=160),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=33, end_frame=33),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=36, end_frame=36),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=80, end_frame=80),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.team_3, start_frame=81, end_frame=81),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=130, end_frame=130),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=133.0, end_frame=133.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3, start_frame=176, end_frame=176),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.team_3, start_frame=188.1, end_frame=188.1),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=38, end_frame=38),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=41.0, end_frame=41.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=75, end_frame=75),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=76, end_frame=76),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=152, end_frame=152),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0, start_frame=153, end_frame=153),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0, start_frame=182, end_frame=182),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_0, start_frame=188.0, end_frame=188.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=32, end_frame=32),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=33, end_frame=33),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=129, end_frame=129),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=130, end_frame=130),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1, start_frame=171.0, end_frame=171.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1, start_frame=174, end_frame=174),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=60, end_frame=60),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=62, end_frame=62),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=100, end_frame=100),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=104, end_frame=104),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=143, end_frame=143),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2, start_frame=149, end_frame=149),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2, start_frame=174, end_frame=174),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_2, start_frame=175, end_frame=175),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=31, end_frame=31),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_3, start_frame=35, end_frame=35),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=59, end_frame=59),
            SpecialWeaponEvent(type=SpecialWeaponEventType.SPOILED, player=self.enemy_3, start_frame=70, end_frame=70),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=94, end_frame=94),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=97.0, end_frame=97.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3, start_frame=117.0, end_frame=117.0),
            SpecialWeaponEvent(type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3, start_frame=119.1, end_frame=119.1),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['kusaya']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageKusaya(method, movie_file=movie_file))

if __name__ == "__main__":
    init()
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)