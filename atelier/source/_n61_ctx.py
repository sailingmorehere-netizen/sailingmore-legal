import re
def show(f, pat, a=60, b=700):
    t = open('tmp_n61/' + f).read()
    m = re.search(pat, t)
    print('##', f[:50], '\n', t[max(0, m.start() - a):m.start() + b] if m else 'NO MATCH', '\n')
show('https_www_oltremare_it_campus_vela_ragazzi_2027_.txt', r'Calendario|Le date|Turni')
show('https_www_oltremare_it_leffetto_che_fa_weekend_vela_adriatico_2027_.txt', r'Calendario|Le date|Quando')
show('https_www_oltremare_it_apnea_a_vela_luglio_2027_.txt', r'Quando|Le date|Date')
show('https_www_oltremare_it_corso_regata_2_.txt', r'Le date', 20, 900)
show('https_tiptopsailing_nl_zeilvakanties_flottielje_zeilen_flottielje_zeilen_lefkas_.txt', r'seizoen 2027 17', 20, 400)
show('https_tiptopsailing_nl_zeilvakanties_kroatie_.txt', r'Afvaart data 2027', 0, 900)
show('https_tiptopsailing_nl_zeilvakanties_lefkas_meezeilen_.txt', r'seizoen 2027|2027', 0, 500)
show('https_tiptopsailing_nl_flottielje_zeilen_corfu_.txt', r'Afvaartdata|afvaartdata', 0, 600)
show('https_www_zeilschoolup_nl_zeilkampen_instructeursopleiding.txt', r'Methodiekweekend', 0, 1200)
