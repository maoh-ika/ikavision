import unittest
from tests.analyzer_test_base import AnalyzerTestBase
from tests.config import config
from battle_analyzer import init
from models.battle import BattleRule, BattleSide, BattleStage, BattleWinLose
from models.ink_color import InkColor
from models.ika_player import IkaPlayer
from models.buki import MainWeapon, SubWeapon, SpecialWeapon, Buki
from events.kill_event import KillEvent
from events.death_event import DeathEvent, DeathReasonType
from events.special_weapon_event import SpecialWeaponEvent, SpecialWeaponEventType

class TestBattleStageMasaba(AnalyzerTestBase):
    initialized = False

    def __init__(self, runTest: str, movie_file: str):
        super().__init__(runTest, movie_file)
        self.team_0 = IkaPlayer(name='まおういか', lamp_ord=0, side=BattleSide.TEAM, id='', nickname='')
        self.team_1 = IkaPlayer(name='き', lamp_ord=1, side=BattleSide.TEAM, id='', nickname='')
        self.team_2 = IkaPlayer(name='*Setumu*ch', lamp_ord=2, side=BattleSide.TEAM, id='', nickname='')
        self.team_3 = IkaPlayer(name='しまくん', lamp_ord=3, side=BattleSide.TEAM, id='', nickname='')
        self.enemy_0 = IkaPlayer(name='BlackLotus', lamp_ord=0, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_1 = IkaPlayer(name='カフェインゼロ', lamp_ord=1, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_2 = IkaPlayer(name='ゆーり', lamp_ord=2, side=BattleSide.ENEMY, id='', nickname='')
        self.enemy_3 = IkaPlayer(name='キャラメルマキアート', lamp_ord=3, side=BattleSide.ENEMY, id='', nickname='')
    
    def _set_initialized(self):
        TestBattleStageMasaba.initialized = True
    
    def _is_initialized(self):
        return TestBattleStageMasaba.initialized

    def test_open_event(self):
        self._test_open_event(
            start_second_expected=0,
            end_second_expected=3
        )
        
    def test_end_event(self):
        self._test_end_event(
            start_second_expected=193,
            end_second_expected=197
        )
    
    def test_result_event(self):
        self._test_result_event(
            start_second_expected=202,
            end_second_expected=205,
            win_lose_expected=BattleWinLose.WIN,
            team_count_expected=52.5,
            enemy_count_expected=37.9,
            count_places=1
        )

    def test_rule(self):
        self._test_rule(BattleRule.NAWABARI)

    def test_stage(self):
        self._test_stage(BattleStage.MASABA)

    def test_team_players(self):
        self._test_team_players([self.team_0, self.team_1, self.team_2, self.team_3])
    
    def test_enemy_players(self):
        self._test_enemy_players([self.enemy_0, self.enemy_1, self.enemy_2, self.enemy_3])

    def test_team_color(self):
        self._test_team_color(InkColor((93, 210, 178)))
    
    def test_enemy_color(self):
        self._test_enemy_color(InkColor((180, 71, 180)))

    def test_team_buki(self):
        self._test_team_buki([
            Buki(main_weapon=MainWeapon.DAPPLE_DUALIES_NOUVEAU, sub_weapon=SubWeapon.TORPEDE, sp_weapon=SpecialWeapon.SAME_RIDE),
            Buki(main_weapon=MainWeapon.BOTTOLE_KAISER_FOIL, sub_weapon=SubWeapon.ROBOT_BOMB, sp_weapon=SpecialWeapon.SUMINAGA_SHEET),
            Buki(main_weapon=MainWeapon.SPLA_ROLLER_COLLABO, sub_weapon=SubWeapon.JUMP_BEACON, sp_weapon=SpecialWeapon.TEIOH_IKA),
            Buki(main_weapon=MainWeapon.SHARP_MARKER, sub_weapon=SubWeapon.QUICK_BOMB, sp_weapon=SpecialWeapon.KANI_TANK),
        ])
    
    def test_enemy_buki(self):
        self._test_enemy_buki([
            Buki(main_weapon=MainWeapon._52GALLON, sub_weapon=SubWeapon.SPLASH_SHIELD, sp_weapon=SpecialWeapon.MEGAPHONE_LASER_51CH),
            Buki(main_weapon=MainWeapon.HISSEN, sub_weapon=SubWeapon.POISON_MIST, sp_weapon=SpecialWeapon.JET_PACK),
            Buki(main_weapon=MainWeapon.BUCKET_SLOSHER, sub_weapon=SubWeapon.SPLASH_BOMB, sp_weapon=SpecialWeapon.TRIPLE_TORNADE),
            Buki(main_weapon=MainWeapon.CLASSIC_SQUIFFER, sub_weapon=SubWeapon.POINT_SENSOR, sp_weapon=SpecialWeapon.GREAT_BARRIER),
        ])

    def test_main_player(self):
        self._test_main_player(0)

    def test_kill_event(self):
        self._test_kill_event([
            KillEvent(start_frame=88, end_frame=93, death_player=self.enemy_2, kill_player=self.team_0),
            KillEvent(start_frame=117, end_frame=122, death_player=self.enemy_1, kill_player=self.team_0),
            KillEvent(start_frame=147, end_frame=152, death_player=self.enemy_2, kill_player=self.team_0)
        ])
    
    def test_death_event(self):
        self._test_death_event([
            DeathEvent(start_frame=42, end_frame=50, death_player=self.team_0, kill_player=self.enemy_0, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon._52GALLON)),
            DeathEvent(start_frame=89, end_frame=96, death_player=self.team_0, kill_player=self.enemy_2, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.BUCKET_SLOSHER)),
            DeathEvent(start_frame=117.1, end_frame=124, death_player=self.team_0, kill_player=self.enemy_1, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.HISSEN)),
            DeathEvent(start_frame=148, end_frame=155, death_player=self.team_0, kill_player=self.enemy_0, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon._52GALLON)),
            DeathEvent(start_frame=176.1, end_frame=182, death_player=self.team_0, kill_player=self.enemy_1, reason_type=DeathReasonType.MAIN_WEAPON, death_reason=Buki.get_buki_id(MainWeapon.HISSEN)),
            DeathEvent(start_frame=47, end_frame=55, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=97.2, end_frame=104, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=111, end_frame=119, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=176.2, end_frame=183, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=192.0, end_frame=192, death_player=self.team_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=29, end_frame=37, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=56, end_frame=63, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=97.3, end_frame=104, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=154, end_frame=162, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=170, end_frame=178, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=193, end_frame=193, death_player=self.team_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=97.1, end_frame=105, death_player=self.team_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=96, end_frame=103, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=172, end_frame=179, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=192.1, end_frame=193, death_player=self.enemy_0, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=53, end_frame=60, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=76, end_frame=84, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=97.0, end_frame=103, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=117.0, end_frame=124, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=130, end_frame=137, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=142.1, end_frame=150, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=161, end_frame=168, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=176.0, end_frame=183, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=191 , end_frame=193, death_player=self.enemy_1, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=54, end_frame=62, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=89, end_frame=95, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=126, end_frame=134, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=147, end_frame=153, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=174, end_frame=180, death_player=self.enemy_2, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=129, end_frame=137, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=142.0, end_frame=149, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
            DeathEvent(start_frame=158, end_frame=165, death_player=self.enemy_3, kill_player=None, reason_type=DeathReasonType.UNKNOWN, death_reason=''),
        ])
    
    def test_sp_event(self):
        self._test_sp_event([
            SpecialWeaponEvent(start_frame=32, end_frame=32, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=39, end_frame=39, type=SpecialWeaponEventType.TRIGGERED, player=self.team_0),
            SpecialWeaponEvent(start_frame=88.0, end_frame=88.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=88.1, end_frame=88.1, type=SpecialWeaponEventType.SPOILED, player=self.team_0),
            SpecialWeaponEvent(start_frame=143, end_frame=143, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=148, end_frame=148, type=SpecialWeaponEventType.SPOILED, player=self.team_0),
            SpecialWeaponEvent(start_frame=173, end_frame=173, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_0),
            SpecialWeaponEvent(start_frame=176, end_frame=176, type=SpecialWeaponEventType.SPOILED, player=self.team_0),
            SpecialWeaponEvent(start_frame=42, end_frame=42, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=43, end_frame=43, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=157, end_frame=157, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_1),
            SpecialWeaponEvent(start_frame=165, end_frame=165, type=SpecialWeaponEventType.TRIGGERED, player=self.team_1),
            SpecialWeaponEvent(start_frame=31.2, end_frame=31.2, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=47, end_frame=47, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=94, end_frame=94, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=96, end_frame=96, type=SpecialWeaponEventType.SPOILED, player=self.team_3),
            SpecialWeaponEvent(start_frame=132.0, end_frame=132.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=132.1, end_frame=132.1, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=165, end_frame=165, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.team_3),
            SpecialWeaponEvent(start_frame=170, end_frame=170, type=SpecialWeaponEventType.TRIGGERED, player=self.team_3),
            SpecialWeaponEvent(start_frame=31.0, end_frame=31.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=34, end_frame=34, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=72.0, end_frame=72.0, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=72.2, end_frame=72.2, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=147, end_frame=147, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=149, end_frame=149, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_0),
            SpecialWeaponEvent(start_frame=31.1, end_frame=31.1, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=32.0, end_frame=32.0, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_1),
            SpecialWeaponEvent(start_frame=50, end_frame=50, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=53, end_frame=53, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_2),
            SpecialWeaponEvent(start_frame=34, end_frame=34, type=SpecialWeaponEventType.FULLY_CHARGED, player=self.enemy_3),
            SpecialWeaponEvent(start_frame=72.1, end_frame=72.1, type=SpecialWeaponEventType.TRIGGERED, player=self.enemy_3)
        ])

def add_tests(suite: unittest.TestSuite):
    movie_file = config['stages']['masaba']
    for method in config['test_methods']:
        suite.addTest(TestBattleStageMasaba(method, movie_file=movie_file))

if __name__ == "__main__":
    init()
    runner = unittest.TextTestRunner(failfast=False)
    suite = unittest.TestSuite()
    add_tests(suite)
    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)