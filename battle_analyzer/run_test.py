import unittest
import multiprocessing
from log import create_prod_logger
from battle_analyzer import init
from tests.test_battle_rule_nawabari import add_tests as add_rule_nawabari
from tests.test_battle_rule_asari_count import add_tests as add_rule_asari_count
from tests.test_battle_rule_hoko_count import add_tests as add_rule_hoko_count
from tests.test_battle_rule_yagura_knockout import add_tests as add_rule_yagura_knockout
from tests.test_battle_stage_kinmedai import add_tests as add_stage_kinmedai
from tests.test_battle_stage_kusaya import add_tests as add_stage_kusaya
from tests.test_battle_stage_yunohana import add_tests as add_stage_yunohana
from tests.test_battle_stage_gonzui import add_tests as add_stage_gonzui
from tests.test_battle_stage_negitoro import add_tests as add_stage_negitoro
from tests.test_battle_stage_bangaitei import add_tests as add_stage_bangaitei
from tests.test_battle_stage_mahimahi import add_tests as add_stage_mahimahi
from tests.test_battle_stage_nampula import add_tests as add_stage_nampula
from tests.test_battle_stage_zatou import add_tests as add_stage_zatou
from tests.test_battle_stage_amabi import add_tests as add_stage_amabi
from tests.test_battle_stage_namerou import add_tests as add_stage_namerou
from tests.test_battle_stage_masaba import add_tests as add_stage_masaba
from tests.test_battle_stage_mategai import add_tests as add_stage_mategai
from tests.test_battle_stage_ohyou import add_tests as add_stage_ohyou
from tests.test_battle_stage_takaashi import add_tests as add_stage_takaashi
from tests.test_battle_stage_sumeshi import add_tests as add_stage_sumeshi
from tests.test_battle_stage_taraport import add_tests as add_stage_taraport
from tests.test_battle_stage_yagara import add_tests as add_stage_yagara

if __name__ == '__main__':
    init()
    create_prod_logger('test')
    loader = unittest.TestLoader()

    suite = unittest.TestSuite()

    # nawabari
    add_rule_nawabari(suite)
    add_rule_asari_count(suite)
    add_rule_hoko_count(suite)
    add_rule_yagura_knockout(suite)

    # stage
    add_stage_kinmedai(suite)
    add_stage_kusaya(suite)
    add_stage_yunohana(suite)
    add_stage_gonzui(suite)
    add_stage_negitoro(suite)
    add_stage_bangaitei(suite)
    add_stage_mahimahi(suite)
    add_stage_nampula(suite)
    add_stage_zatou(suite)
    add_stage_amabi(suite)
    add_stage_namerou(suite)
    add_stage_masaba(suite)
    add_stage_mategai(suite)
    add_stage_ohyou(suite)
    add_stage_takaashi(suite)
    add_stage_sumeshi(suite)
    add_stage_taraport(suite)
    add_stage_yagara(suite)

    runner = unittest.TextTestRunner(failfast=False)
    result = runner.run(suite)