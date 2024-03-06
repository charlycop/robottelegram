import re

texte = """
XTZ (LONG)

Prix d'entré : 1,335-1,425

TP :
1,46
1,51
1,56
1,62
1,78
2,00

SL : 1,10
"""

# Définition du dictionnaire pour stocker les données
donnees = {}

# Extraction du symbole
donnees['Symbole'] = re.search(r'([A-Z]+)', texte).group(0) + "USDT"

# Extraction du type de transaction
donnees['Type de transaction'] = re.search(r'\((\w+)\)', texte).group(1)

# Extraction des prix d'entrée
prix_entree = re.findall(r'\d+,\d+', texte)[:2]
donnees['Prix entrée'] = [float(p.replace(',', '.')) for p in prix_entree]

# Extraction des TP
tps = re.findall(r'\d+,\d+', re.search(r'TP :([\s\S]+?)SL', texte).group(1))
donnees['TP'] = [float(tp.replace(',', '.')) for tp in tps]

# Extraction du SL
donnees['SL'] = float(re.search(r'SL : (\d+,\d+)', texte).group(1).replace(',', '.'))

# Création de la chaîne multiligne
resultat = f"""Symbole : {donnees['Symbole']}
Type de transaction : {donnees['Type de transaction']}
Prix d'entrées : {donnees['Prix entrée']}
TP : {donnees['TP']}
SL : {donnees['SL']}"""

# Affichage du résultat
print(resultat)