s = open('projets/sailingmore/site/stages.html', encoding='utf-8').read()
for k in ['function cmpPos(i){', '"ajouter"', 'Quatre offres', 'sm-comparatif']:
    print(k, s.count(k))
i = s.find('"ajouter"')
print(s[i - 120:i + 80])
i = s.find('function cmpPos')
print(s[i - 120:i])
import glob
print(glob.glob('**/clics_sortants*', recursive=True)[:5])
