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

class TestBattleRuleCyozameKnockout(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='ウンイ', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='まおういか', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='くろしろ', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='みせいねん', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleRuleCyozameKnockout.initialized = True
    
    def _is_initialized(self):
        return TestBattleRuleCyozameKnockout.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=66,
            end_second_expected=71
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=76,
            end_second_expected=79,
            win_lose_expected=BattleWinLose.LOSE,
            team_count_expected=0,
            enemy_count_expected=100,
            count_places=0
        )

    def test_rule(self):
        self._test_rule(BattleRule.YAGURA)

    def test_stage(self):
        self._test_stage(BattleStage.CYOUZAME)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, None, None])
    
    def test_enemy_players(self):
        self._test_enemy_players([None, None, self.enemy_0, self.enemy_1])

    def test_team_color(self):
        self._test_team_color(InkColor((123, 81, 191)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((177, 201, 100)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.VINCENT_NOUVEAU, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.MULTI_MISSILE),
            Buki(main_weapon=MainWeapon.SPLA_SHOOTER_COLLABO, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            None,
            None
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            None,
            None,
            Buki(main_weapon=MainWeapon.HERO_SHOOTER_REPLICA, sub_weapon=SubWeapon.KYUUBAN_BOMB, sp_weapon=SpecialWeapon.ULTRA_SHOOT),
            Buki(main_weapon=MainWeapon.HOT_BLASTER_CUSTOM, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.ULTRA_TYAKUTI),
        ])

    def test_main_player(self):
        self._test_main_player(1)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(start_frame=26, end_frame=31, death_player=self.enemy_0, kill_player=self.team_1),
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(start_frame=27, end_frame=35, death_player=self.team_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=52, end_frame=60, death_player=self.team_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=26, end_frame=34, death_player=self.team_1, kill_player=self.enemy_1, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.QUAD_HOPPER_BLACK)),
            DeathEvent(start_frame=44, end_frame=34, death_player=self.team_1, kill_player=self.enemy_1, reason_type=DeathReasonType.SP_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.QUAD_HOPPER_BLACK)),
            DeathEvent(start_frame=26, end_frame=34, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=64.0, end_frame=64.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=64.1, end_frame=64.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=36, end_frame=36, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=42, end_frame=42, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['cyozame']
    for method in config['test_methods']:
        suite.addTest(TestBattleRuleCyozameKnockout(method, movie_file=movie_file))

if __name__ == "__main__":
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)