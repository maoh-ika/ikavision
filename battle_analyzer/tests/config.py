config = {
    'rules': {
        'nawabari': 'battle_analyzer/tests/testdata/test_nawabari_konbu_20231116_112401_y4dF95obSrQ.mp4',
        'asari': {
            'count': 'battle_analyzer/tests/testdata/test_asari_bangaitei_count_20231210_130506_xvhZkvfgVXU.mp4'
        },
        'yagura': {
            'knockout': 'battle_analyzer/tests/testdata/test_yagura_mantamaria_knockout_20231216_012940_X1kcrgQx_M4.mp4'
        },
        'hoko': {
            'count': 'battle_analyzer/tests/testdata/test_hoko_hirame_count_20231210_125811_OH7rilxETp0.mp4'
        }
    },
    'stages': {
        'kinmedai': 'battle_analyzer/tests/testdata/test_nawabari_kinmedai_20231118_205716_-u3lfJnlU9A.mp4',
        'kusaya': 'battle_analyzer/tests/testdata/test_nawabari_kusaya_20231116_112401_-4M4jcCrVy4.mp4',
        'yunohana': 'battle_analyzer/tests/testdata/test_nawabari_yunohana_20231118_203728_KomVrrSZOJo.mp4',
        'gonzui': 'battle_analyzer/tests/testdata/test_hoko_gonzui_knockout_20231209_122159_WdRFE5uiCng.mp4',
        'negitoro': 'battle_analyzer/tests/testdata/test_area_negitoro_knockout_20231206_224652_Rt1LFg2On5Q.mp4',
        'bangaitei': 'battle_analyzer/tests/testdata/test_nawabari_bangaitei_20231210_122146_USAnC-iz7Mk.mp4',
        'mahimahi': 'battle_analyzer/tests/testdata/test_nawabari_mahimahi_20231213_192955_Wua3soL3doM.mp4',
        'masaba': 'battle_analyzer/tests/testdata/test_nawabari_masaba_20231213_193535_lo-NWWQ2G3c.mp4',
        'nampula': 'battle_analyzer/tests/testdata/test_area_nampula_count_20231213_214811_g_2bFP8rpA8.mp4',
        'namerou': 'battle_analyzer/tests/testdata/test_nawabari_namerou_20231216 014444_uLA1EJMcU2I.mp4',
        'taraport': 'battle_analyzer/tests/testdata/test_nawabari_taraport_20231216_013949_ToR3MhuQIs0.mp4',
        'zatou': 'battle_analyzer/tests/testdata/test_yagura_zatou_count_20231219_121628_Iwj9YjkW5LY.mp4',
        'takaashi': 'battle_analyzer/tests/testdata/test_yagura_takaashi_knockout_20231218_235423_riXN5btAvqE.mp4',
        'amabi': 'battle_analyzer/tests/testdata/test_nawabari_amabi_20231220_193846_Lolo1kojmV0.mp4',
        'ohyou': 'battle_analyzer/tests/testdata/test_nawabari_ohyou_20231221_132631_8h48jXKjqms.mp4',
        'yagara': 'battle_analyzer/tests/testdata/test_nawabari_yagara_20231220_193307_rtq7InME3kE.mp4',
        'cyozame': 'battle_analyzer/tests/testdata/test_yagura_cyozame_knockout_20231226_111055_ms18nvCi_Sw.mp4',
        'mategai': 'battle_analyzer/tests/testdata/test_nawabari_mategai_20231228_230440_gT7p5T_KfU8.mp4',
        'sumeshi': 'battle_analyzer/tests/testdata/test_nawabari_sumeshi_20231228_230846_2sG1j_wkLds.mp4',
    },
    'test_methods': [
        'test_open_event',
        'test_end_event',
        'test_result_event',
        'test_rule',
        'test_stage',
        'test_team_players',
        'test_enemy_players',
        'test_team_color',
        'test_enemy_color',
        'test_team_buki',
        'test_enemy_buki',
        'test_main_player',
        'test_kill_event',
        'test_death_event',
        'test_sp_event'
    ]
}