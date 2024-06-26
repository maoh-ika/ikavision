from move_classification_files import move_files

kana_list = [
    'diacritical_a_grave',
    'diacritical_a_acute',
    'diacritical_a_circumflex',
    'diacritical_a_tilde',
    'diacritical_a_umlaut',
    'diacritical_a_ring',
    'diacritical_a_ash',
    'diacritical_a_macron',
    'diacritical_a_brave',
    'diacritical_a_ogonek',
    'diacritical_c_cedilla',
    'diacritical_c_acute',
    'diacritical_c_dot',
    'diacritical_c_caron',
    'diacritical_d_stroke',
    'diacritical_d_caron',
    'diacritical_dz_caron',
    'diacritical_dz',
    'diacritical_e_grave',
    'diacritical_e_acute',
    'diacritical_e_circumflex',
    'diacritical_e_umlaut',
    'diacritical_e_trema',
    'diacritical_e_macron',
    'diacritical_e_ogonek',
    'diacritical_e_caron',
    'diacritical_g_breve',
    'diacritical_g_dot',
    'diacritical_g_commaabove',
    'diacritical_h_stroke',
    'diacritical_i_grave',
    'diacritical_i_acute',
    'diacritical_i_circumflex',
    'diacritical_i_umlaut',
    'diacritical_i_macron',
    'diacritical_i_ogonek',
    'diacritical_k_comma',
    'diacritical_l_acute',
    'diacritical_l_commabelow',
    'diacritical_l_caron',
    'diacritical_l_stroke',
    'diacritical_n_tilde',
    'diacritical_n_acute',
    'diacritical_n_commabelow',
    'diacritical_n_caron',
    'diacritical_o_grave',
    'diacritical_o_acute',
    'diacritical_o_circumflex',
    'diacritical_o_tilde',
    'diacritical_o_umlaut',
    'diacritical_o_stroke',
    'diacritical_o_e',
    'diacritical_o_doubleacute',
    'diacritical_o_macron',
    'diacritical_r_acute',
    'diacritical_r_caron',
    'diacritical_s_caron',
    'diacritical_s_stroke',
    'diacritical_s_acute',
    'diacritical_s_cedilla',
    'diacritical_p_stroke',
    'diacritical_t_caron',
    'diacritical_t_commabelow',
    'diacritical_u_grave',
    'diacritical_u_acute',
    'diacritical_u_circumflex',
    'diacritical_u_umlaut',
    'diacritical_u_macron',
    'diacritical_u_ring',
    'diacritical_u_doubleacute',
    'diacritical_u_ogonek',
    'diacritical_y_acute',
    'diacritical_y_trema',
    'diacritical_z_acute',
    'diacritical_z_dot',
    'diacritical_z_caron',
    'diacritical_a_grave_upper',
    'diacritical_a_acute_upper',
    'diacritical_a_circumflex_upper',
    'diacritical_a_tilde_upper',
    'diacritical_a_umlaut_upper',
    'diacritical_a_ring_upper',
    'diacritical_a_ash_upper',
    'diacritical_a_macron_upper',
    'diacritical_a_brave_upper',
    'diacritical_a_ogonek_upper',
    'diacritical_c_cedilla_upper',
    'diacritical_c_acute_upper',
    'diacritical_c_dot_upper',
    'diacritical_c_caron_upper',
    'diacritical_d_stroke_upper',
    'diacritical_d_caron_upper',
    'diacritical_dz_caron_upper',
    'diacritical_dz_upper',
    'diacritical_e_grave_upper',
    'diacritical_e_acute_upper',
    'diacritical_e_circumflex_upper',
    'diacritical_e_umlaut_upper',
    'diacritical_e_macron_upper',
    'diacritical_e_ogonek_upper',
    'diacritical_e_caron_upper',
    'diacritical_g_breve_upper',
    'diacritical_g_dot_upper',
    'diacritical_g_cedilla_upper',
    'diacritical_h_stroke_upper',
    'diacritical_i_grave_upper',
    'diacritical_i_acute_upper',
    'diacritical_i_circumflex_upper',
    'diacritical_i_umlaut_upper',
    'diacritical_i_macron_upper',
    'diacritical_i_ogonek_upper',
    'diacritical_k_cedilla_upper',
    'diacritical_l_acute_upper',
    'diacritical_l_cedilla_upper',
    'diacritical_l_caron_upper',
    'diacritical_l_stroke_upper',
    'diacritical_n_tilde_upper',
    'diacritical_n_acute_upper',
    'diacritical_n_commabelow_upper',
    'diacritical_n_caron_upper',
    'diacritical_o_grave_upper',
    'diacritical_o_acute_upper',
    'diacritical_o_circumflex_upper',
    'diacritical_o_tilde_upper',
    'diacritical_o_umlaut_upper',
    'diacritical_o_stroke_upper',
    'diacritical_o_e_upper',
    'diacritical_o_doubleacute_upper',
    'diacritical_o_macron_upper',
    'diacritical_r_acute_upper',
    'diacritical_r_caron_upper',
    'diacritical_s_caron_upper',
    'diacritical_s_acute_upper',
    'diacritical_s_cedilla_upper',
    'diacritical_p_stroke_upper',
    'diacritical_t_caron_upper',
    'diacritical_t_commabelow_upper',
    'diacritical_u_grave_upper',
    'diacritical_u_acute_upper',
    'diacritical_u_circumflex_upper',
    'diacritical_u_umlaut_upper',
    'diacritical_u_macron_upper',
    'diacritical_u_ring_upper',
    'diacritical_u_doubleacute_upper',
    'diacritical_u_ogonek_upper',
    'diacritical_y_acute_upper',
    'diacritical_y_trema_upper',
    'diacritical_z_acute_upper',
    'diacritical_z_dot_upper',
    'diacritical_z_caron_upper',
]

src_dir = '/Users/maohika/Downloads/char/diacritical/{label}'
dst_dir = '/Volumes/splatoon3/dataset/ocr/diacritical/{label}'
move_files(kana_list, src_dir, dst_dir)
