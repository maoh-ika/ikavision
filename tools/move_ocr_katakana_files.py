from move_classification_files import move_files

kana_list = [
    'katakana_a',
    'katakana_i',
    'katakana_u',
    'katakana_e',
    'katakana_o',
    'katakana_ka',
    'katakana_ki',
    'katakana_ku',
    'katakana_ke',
    'katakana_ko',
    'katakana_ga',
    'katakana_gi',
    'katakana_gu',
    'katakana_ge',
    'katakana_go',
    'katakana_sa',
    'katakana_si',
    'katakana_su',
    'katakana_se',
    'katakana_so',
    'katakana_za',
    'katakana_zi',
    'katakana_zu',
    'katakana_ze',
    'katakana_zo',
    'katakana_ta',
    'katakana_ti',
    'katakana_tu',
    'katakana_te',
    'katakana_to',
    'katakana_da',
    'katakana_di',
    'katakana_du',
    'katakana_de',
    'katakana_do',
    'katakana_na',
    'katakana_ni',
    'katakana_nu',
    'katakana_ne',
    'katakana_no',
    'katakana_ha',
    'katakana_hi',
    'katakana_hu',
    'katakana_he',
    'katakana_ho',
    'katakana_pa',
    'katakana_pi',
    'katakana_pu',
    'katakana_pe',
    'katakana_po',
    'katakana_ba',
    'katakana_bi',
    'katakana_bu',
    'katakana_be',
    'katakana_bo',
    'katakana_ma',
    'katakana_mi',
    'katakana_mu',
    'katakana_me',
    'katakana_mo',
    'katakana_ya',
    'katakana_yu',
    'katakana_yo',
    'katakana_ra',
    'katakana_ri',
    'katakana_ru',
    'katakana_re',
    'katakana_ro',
    'katakana_wa',
    'katakana_wo',
    'katakana_n',
    'katakana_vu'
]

src_dir = '/Users/maohika/Downloads/char/katakana/{label}'
dst_dir = '/Volumes/splatoon3/dataset/ocr/katakana/{label}'
move_files(kana_list, src_dir, dst_dir)
