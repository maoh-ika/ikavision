from enum import Enum, auto
from dataclasses import dataclass
import os
import json
from error import InternalError

main_labels = {
    'bold_marker': 'ボールドマーカー',
    'bold_marker_neo': 'ボールドマーカーネオ',
    'wakaba_shooter': 'わかばシューター',
    'momiji_shooter': 'もみじシューター',
    'promodeler_mg': 'プロモデラーMG',
    'promodeler_rg': 'プロモデラーRG',
    'sharp_marker': 'シャープマーカー',
    'sharp_marker_neo': 'シャープマーカーネオ',
    'spla_shooter': 'スプラシューター',
    'hero_shooter_replica': 'ヒーローシューターレプリカ',
    'spla_shooter_collabo': 'スプラシューターコラボ',
    'nzap85': 'N-ZAP85',
    'nzap89': 'N-ZAP89',
    '52gallon': '.52ガロン',
    'prime_shooter': 'プライムシューター',
    'prime_shooter_collabo': 'プライムシューターコラボ',
    '96gallon': '.96ガロン',
    '96gallon_deco': '.96ガロンデコ',
    'jet_sweeper': 'ジェットスイーパー',
    'jet_sweeper_custom': 'ジェットスイーパーカスタム',
    'space_shooter': 'スペースシューター',
    'space_shooter_collabo': 'スペースシューターコラボ',
    'l3_reelgun': 'L3リールガン',
    'l3_reelgun_d': 'L3リールガンD',
    'h3_reelgun': 'H3リールガン',
    'h3_reelgun_d': 'H3リールガンD',
    'bottole_kaiser': 'ボトルガイザー',
    'carbon_roller': 'カーボンローラー',
    'carbon_roller_deco': 'カーボンローラーデコ',
    'spla_roller': 'スプラローラー',
    'spla_roller_collabo': 'スプラローラーコラボ',
    'dynamo_roller': 'ダイナモローラー',
    'dynamo_roller_tesla': 'ダイナモローラーテスラ',
    'variable_roller': 'ヴァリアブルローラー',
    'wide_roller': 'ワイドローラー',
    'wide_roller_collabo': 'ワイドローラーコラボ',
    'classic_squiffer': 'スクイックリンα',
    'spla_charger': 'スプラチャージャー',
    'spla_scope': 'スプラスコープ',
    'spla_charger_collabo': 'スプラチャージャーコラボ',
    'spla_scope_collabo': 'スプラスコープコラボ',
    'eliter_4k': 'リッター4K',
    '4k_scope': '4Kスコープ',
    '14shiki_takedutsu_kou': '14式竹筒銃・甲',
    'soy_tuber': 'ソイチューバー',
    'soy_tuber_custom': 'ソイチューバーカスタム',
    'rpen_5h': 'R-PEN/5H',
    'nova_blaster': 'ノヴァブラスター',
    'nova_blaster_neo': 'ノヴァブラスターネオ',
    'hot_blaster': 'ホットブラスター',
    'long_blaster': 'ロングブラスター',
    'rapid_blaster': 'ラピッドブラスター',
    'rapid_blaster_deco': 'ラピッドブラスターデコ',
    'r_blaster_elite': 'Rブラスターエリート',
    'r_blaster_elite_deco': 'Rブラスターエリートデコ',
    'crash_blaster': 'クラッシュブラスター',
    'crash_blaster_neo': 'クラッシュブラスターネオ',
    'sblast92': 'S-BLAST92',
    'hissen': 'ヒッセン',
    'hissen_nouveau': 'ヒッセン・ヒュー',
    'bucket_slosher': 'バケットスロッシャー',
    'bucket_slosher_deco': 'バケットスロッシャーデコ',
    'screw_slosher': 'スクリュースロッシャー',
    'screw_slosher_neo': 'スクリュースロッシャーネオ',
    'over_flosher': 'オーバーフロッシャー',
    'over_flosher_deco': 'オーバーフロッシャーデコ',
    'explosher': 'エクスプロッシャー',
    'spla_spiner': 'スプラスピナー',
    'spla_spiner_collabo': 'スプラスピナーコラボ',
    'barrel_spiner': 'バレルスピナー',
    'barrel_spiner_deco': 'バレルスピナーデコ',
    'hydrant': 'ハイドラント',
    'kugelschreiber': 'クーゲルシュライバー',
    'kugelschreiber_nouveau': 'クーゲルシュライバー・ヒュー',
    'nautilus47': 'ノーチラス47',
    'pablo': 'パブロ',
    'pablo_nouveau': 'パブロ・ヒュー',
    'hokusai': 'ホクサイ',
    'hokusai_nouveau': 'ホクサイ・ヒュー',
    'vincent': 'フィンセント',
    'dapple_dualies': 'スパッタリー',
    'dapple_dualies_nouveau': 'スパッタリー・ヒュー',
    'spla_maneuver': 'スプラマニューバー',
    'dual_sweeper': 'デュアルスイーパー',
    'dual_sweeper_custom': 'デュアルスイーパーカスタム',
    'kelvin535': 'ケルビン525',
    'quad_hopper_black': 'クアッドホッパーブラック',
    'quad_hopper_white': 'クアッドホッパーホワイト',
    'para_shelter': 'パラシェルター',
    'para_shelter_solare': 'パラシェルターソレーラ',
    'camping_shelter': 'キャンピングシェルター',
    'camping_shelter_solare': 'キャンピングシェルターソレーラ',
    'spy_gadget': 'スパイガジェット',
    'tri_stringer': 'トライストリンガー',
    'tri_stringer_collabo': 'トライストリンガーコラボ',
    'lact450': 'LACT-450',
    'drive_wiper': 'ドライブワイパー',
    'drive_wiper_deco': 'ドライブワイパーデコ',
    'gym_wiper': 'ジムワイパー',
    'examiner': 'イグザミナー',
    'moplin': 'モップリン',
    'bottole_kaiser_foil': 'ボトルガイザーフォイル',
    'gym_wiper_nouveau': 'ジムワイパー・ヒュー',
    'hot_blaster_custom': 'ホットブラスターカスタム',
    'lact450_deco': 'LACT-450デコ',
    'rpen_5b': 'R-PEN/5B',
    'sblast91': 'S-BLAST91',
    'spla_maneuver_collabo': 'スプラマニューバーコラボ',
    'spy_gadget_solare': 'スパイガジェットソレーラ',
    'vincent_nouveau': 'フィンセント・ヒュー',
    'octa_shooter_replica': 'オクタシューターレプリカ',
    'order_blaster_replica': 'オーダーブラスターレプリカ',
    'order_brush_replica': 'オーダーブラシレプリカ',
    'order_charger_replica': 'オーダーチャージャーレプリカ',
    'order_maneuver_replica': 'オーダーマニューバーレプリカ',
    'order_roller_replica': 'オーダーローラーレプリカ',
    'order_shelter_replica': 'オーダーシェルターレプリカ',
    'order_shooter_replica': 'オーダーシューターレプリカ',
    'order_spinner_replica': 'オーダースピナーレプリカ',
    'order_stringer_replica': 'オーダーストリンガーレプリカ',
    'order_wiper_replica': 'オーダーワイパーレプリカ',
    'classic_squiffer_beta': 'スクイックリンβ',
    '24shiki_harikaegasa_kou': '24式張替傘・甲',
    '52gallon_deco': '.52ガロンデコ',
    'moplin_d': 'モップリンD',
    'eliter_4k_custom': 'リッター4Kカスタム',
    'gaen_ff': 'ガエンFF',
    'variable_roller_foil': 'ヴァリアブルローラーフォイル',
    '4k_scope_custom': '4Kスコープカスタム',
    'nautilus79': 'ノーチラス79',
    'explosher_custom': 'エクスプロッシャーカスタム',
    'kelvin525_deco': 'ケルビン525デコ',
}

sub_labels = {
    'splash_bomb': 'スプラッシュボム',
    'kyuuban_bomb': 'キューバンボム',
    'quick_bomb': 'クイックボム',
    'sprinkler': 'スプリンクラー',
    'splash_shield': 'スプラッシュシールド',
    'tansan_bomb': 'タンサンボム',
    'curling_bomb': 'カーリングボム',
    'robot_bomb': 'ロボットボム',
    'jump_beacon': 'ジャンプビーコン',
    'point_sensor': 'ポイントセンサー',
    'trap': 'トラップ',
    'poison_mist': 'ポイズンミスト',
    'line_marker': 'ラインマーカー',
    'torpede': 'トーピード'
}

sp_labels = {
    'kani_tank': 'カニタンク',
    'syoku_wonder': 'ショクワンダー',
    'kyuuinki': 'キューインキ',
    'energy_stand': 'エナジースタンド',
    'hop_sonar': 'ホップソナー',
    'same_ride': 'サメライド',
    'decoy_tirashi': 'デコイチラシ',
    'great_barrier': 'グレートバリア',
    'ultra_shoot': 'ウルトラショット',
    'megaphone_laser_51ch': 'メガホンレーザー5.1ch',
    'triple_tornade': 'トリプルトルネード',
    'teioh_ika': 'テイオウイカ',
    'multi_missile': 'マルチミサイル',
    'jet_pack': 'ジェットパック',
    'amefurashi': 'アメフラシ',
    'ultra_hanko': 'ウルトラハンコ',
    'nice_dama': 'ナイスダマ',
    'ultra_tyakuti': 'ウルトラチャクチ',
    'suminaga_sheet': 'スミナガシート'
}

class MainWeapon(Enum):
    UNKNOWN = auto()
    BOLD_MARKER = auto()
    BOLD_MARKER_NEO = auto()
    WAKABA_SHOOTER = auto()
    MOMIJI_SHOOTER = auto()
    PROMODELER_MG = auto()
    PROMODELER_RG = auto()
    SHARP_MARKER = auto()
    SHARP_MARKER_NEO = auto()
    SPLA_SHOOTER = auto()
    HERO_SHOOTER_REPLICA = auto()
    SPLA_SHOOTER_COLLABO = auto()
    NZAP85 = auto()
    NZAP89 = auto()
    _52GALLON = auto()
    PRIME_SHOOTER = auto()
    PRIME_SHOOTER_COLLABO = auto()
    _96GALLON = auto()
    _96GALLON_DECO = auto()
    JET_SWEEPER = auto()
    JET_SWEEPER_CUSTOM = auto()
    SPACE_SHOOTER = auto()
    SPACE_SHOOTER_COLLABO = auto()
    L3_REELGUN = auto()
    L3_REELGUN_D = auto()
    H3_REELGUN = auto()
    H3_REELGUN_D = auto()
    BOTTOLE_KAISER = auto()
    CARBON_ROLLER = auto()
    CARBON_ROLLER_DECO = auto()
    SPLA_ROLLER = auto()
    SPLA_ROLLER_COLLABO = auto()
    DYNAMO_ROLLER = auto()
    DYNAMO_ROLLER_TESLA = auto()
    VARIABLE_ROLLER = auto()
    WIDE_ROLLER = auto()
    WIDE_ROLLER_COLLABO = auto()
    CLASSIC_SQUIFFER = auto()
    SPLA_CHARGER = auto()
    SPLA_SCOPE = auto()
    SPLA_CHARGER_COLLABO = auto()
    SPLA_SCOPE_COLLABO = auto()
    ELITER_4K = auto()
    _4K_SCOPE = auto()
    _14SHIKI_TAKEDUTSU_KOU = auto()
    SOY_TUBER = auto()
    SOY_TUBER_CUSTOM = auto()
    RPEN_5H = auto()
    NOVA_BLASTER = auto()
    NOVA_BLASTER_NEO = auto()
    HOT_BLASTER = auto()
    LONG_BLASTER = auto()
    RAPID_BLASTER = auto()
    RAPID_BLASTER_DECO = auto()
    R_BLASTER_ELITE = auto()
    R_BLASTER_ELITE_DECO = auto()
    CRASH_BLASTER = auto()
    CRASH_BLASTER_NEO = auto()
    SBLAST92 = auto()
    HISSEN = auto()
    HISSEN_NOUVEAU = auto()
    BUCKET_SLOSHER = auto()
    BUCKET_SLOSHER_DECO = auto()
    SCREW_SLOSHER = auto()
    SCREW_SLOSHER_NEO = auto()
    OVER_FLOSHER = auto()
    OVER_FLOSHER_DECO = auto()
    EXPLOSHER = auto()
    SPLA_SPINER = auto()
    SPLA_SPINER_COLLABO = auto()
    BARREL_SPINER = auto()
    BARREL_SPINER_DECO = auto()
    HYDRANT = auto()
    KUGELSCHREIBER = auto()
    KUGELSCHREIBER_NOUVEAU = auto()
    NAUTILUS47 = auto()
    PABLO = auto()
    PABLO_NOUVEAU = auto()
    HOKUSAI = auto()
    HOKUSAI_NOUVEAU = auto()
    VINCENT = auto()
    DAPPLE_DUALIES = auto()
    DAPPLE_DUALIES_NOUVEAU = auto()
    SPLA_MANEUVER = auto()
    DUAL_SWEEPER = auto()
    DUAL_SWEEPER_CUSTOM = auto()
    KELVIN535 = auto()
    QUAD_HOPPER_BLACK = auto()
    QUAD_HOPPER_WHITE = auto()
    PARA_SHELTER = auto()
    PARA_SHELTER_SOLARE = auto()
    CAMPING_SHELTER = auto()
    CAMPING_SHELTER_SOLARE = auto()
    SPY_GADGET = auto()
    TRI_STRINGER = auto()
    TRI_STRINGER_COLLABO = auto()
    LACT450 = auto()
    DRIVE_WIPER = auto()
    DRIVE_WIPER_DECO = auto()
    GYM_WIPER = auto()
    EXAMINER = auto()
    MOPLIN = auto()
    BOTTOLE_KAISER_FOIL = auto()
    GYM_WIPER_NOUVEAU = auto()
    HOT_BLASTER_CUSTOM = auto()
    LACT450_DECO = auto()
    RPEN_5B = auto()
    SBLAST91 = auto()
    SPLA_MANEUVER_COLLABO = auto()
    SPY_GADGET_SOLARE = auto()
    VINCENT_NOUVEAU = auto()
    OCTA_SHOOTER_REPLICA = auto()
    ORDER_BLASTER_REPLICA = auto()
    ORDER_BRUSH_REPLICA = auto()
    ORDER_CHARGER_REPLICA = auto()
    ORDER_MANEUVER_REPLICA = auto()
    ORDER_ROLLER_REPLICA = auto()
    ORDER_SHELTER_REPLICA = auto()
    ORDER_SHOOTER_REPLICA = auto()
    ORDER_SPINNER_REPLICA = auto()
    ORDER_STRINGER_REPLICA = auto()
    ORDER_WIPER_REPLICA = auto()
    SPLA_MANEUVER_COLLABO = auto()
    SPY_GADGET_SOLARE = auto()
    VINCENT_NOUVEAU = auto()
    OCTA_SHOOTER_REPLICA = auto()
    ORDER_BLASTER_REPLICA = auto()
    ORDER_BRUSH_REPLICA = auto()
    ORDER_CHARGER_REPLICA = auto()
    ORDER_MANEUVER_REPLICA = auto()
    ORDER_ROLLER_REPLICA = auto()
    ORDER_SHELTER_REPLICA = auto()
    ORDER_SHOOTER_REPLICA = auto()
    ORDER_SPINNER_REPLICA = auto()
    ORDER_STRINGER_REPLICA = auto()
    ORDER_WIPER_REPLICA = auto()
    CLASSIC_SQUIFFER_BETA = auto()
    _24SHIKI_HARIKAEGASA_KOU = auto()
    _52GALLON_DECO = auto()

class SubWeapon(Enum):
    UNKNOWN = auto()
    SPLASH_BOMB = auto()
    KYUUBAN_BOMB = auto()
    QUICK_BOMB = auto()
    SPRINKLER = auto()
    SPLASH_SHIELD = auto()
    TANSAN_BOMB = auto()
    CURLING_BOMB = auto()
    ROBOT_BOMB = auto()
    JUMP_BEACON = auto()
    POINT_SENSOR = auto()
    TRAP = auto()
    POISON_MIST = auto()
    LINE_MARKER = auto()
    TORPEDE = auto()

class SpecialWeapon(Enum):
    UNKNOWN = auto()
    KANI_TANK = auto()
    SYOKU_WONDER = auto()
    KYUUINKI = auto()
    ENERGY_STAND = auto()
    HOP_SONAR = auto()
    SAME_RIDE = auto()
    DECOY_TIRASHI = auto()
    GREAT_BARRIER = auto()
    ULTRA_SHOOT = auto()
    MEGAPHONE_LASER_51CH = auto()
    TRIPLE_TORNADE = auto()
    TEIOH_IKA = auto()
    MULTI_MISSILE = auto()
    JET_PACK = auto()
    AMEFURASHI = auto()
    ULTRA_HANKO = auto()
    NICE_DAMA = auto()
    ULTRA_TYAKUTI = auto()
    SUMINAGA_SHEET = auto()


def find_spec_path(weapon_type: str, buki_id: str, battle_date: int) -> str:
    spec_path = os.environ.get('BUKI_SPEC_ROOT')
    weapon_path = f'{spec_path}/{weapon_type}'
    veresions_path = f'{weapon_path}/versions.json'
    if not os.path.exists(veresions_path):
        raise InternalError('versions not found')
    with open(veresions_path, encoding='utf-8') as f:
        versions = json.load(f)
        data_folder = None
        for ver in versions:
            if ver['effectiveDate'] <= battle_date:
                data_folder = ver['dataFolder']
        if data_folder is None:
            data_folder = versions[0]['dataFolder'] # older than the data analyzer have, use oldest
    
    return f'{weapon_path}/{data_folder}/{Buki.get_buki_id(buki_id)}.json'

@dataclass
class Buki:
    main_weapon: MainWeapon = MainWeapon.UNKNOWN
    sub_weapon: SubWeapon = SubWeapon.UNKNOWN
    sp_weapon: SpecialWeapon = SpecialWeapon.UNKNOWN
    sub_ink_consumption_percent: int = 0

    @classmethod
    def create(cls, main: MainWeapon, battle_date: int):
        main_spec_path = find_spec_path('main_weapon', main, battle_date)
        if not os.path.exists(main_spec_path):
            raise InternalError('buki spec not found')

        with open(main_spec_path, encoding='utf-8') as f_main:
            main_spec = json.load(f_main)
            sub_weapon = SubWeapon.__members__.get(main_spec['subWeapon'].upper())
            if sub_weapon is None:
                raise InternalError('unknown sub weapon')
            sp_weapon = SpecialWeapon.__members__.get(main_spec['spWeapon'].upper())
            if sp_weapon is None:
                raise InternalError('unknown sp weapon')
            
            sub_spec_path = find_spec_path('sub_weapon', sub_weapon, battle_date)
            if not os.path.exists(sub_spec_path):
                raise InternalError('buki spec not found')
            with open(sub_spec_path, encoding='utf-8') as f_sub:
                sub_spec = json.load(f_sub)
                sub_ink = sub_spec['inkConsumptionPercent']
                return Buki(
                    main_weapon=main,
                    sub_weapon=sub_weapon,
                    sp_weapon=sp_weapon,
                    sub_ink_consumption_percent=sub_ink
                )

    @staticmethod
    def get_buki_id(wp: Enum):
        name = wp.name[1:] if wp.name.startswith('_') else wp.name
        return name.lower()

    @property
    def main_id(self):
        return Buki.get_buki_id(self.main_weapon) 
    
    @property
    def sub_id(self):
        return Buki.get_buki_id(self.sub_weapon) 
    
    @property
    def sp_id(self):
        return Buki.get_buki_id(self.sp_weapon) 
    
    @property
    def main_label(self):
        return main_labels[Buki.get_buki_id(self.main_weapon)]
    
    @property
    def sub_label(self):
        return sub_labels[Buki.get_buki_id(self.sub_weapon)]
    
    @property
    def sp_label(self):
        return sp_labels[Buki.get_buki_id(self.sp_weapon)]