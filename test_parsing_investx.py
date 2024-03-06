import re

texte = """
⚠️ALERTE⚠️

🟢J’achète CADCHF à 0,6530

❌Stop loss : 0,6435 (95 pips)

💵Take profit 1 : 0,6680
💵Take profit 2 : 0,70



➡️Vidéo sur la gestion des risques : https://t.me/c/1240221457/2725

➡️Tableau des lots que je préconise : https://t.me/c/1240221457/2816
"""

# Définition du dictionnaire pour stocker les données
donnees = {}

# Extraction de la paire de devises
donnees['Paire'] = re.search(r'J’achète (\w+) à', texte).group(1)

# Extraction du prix d'achat
donnees['Prix achat'] = float(re.search(r'à ([\d,]+)', texte).group(1).replace(',', '.'))

# Extraction du stop loss
donnees['Stop loss'] = float(re.search(r'Stop loss : ([\d,]+)', texte).group(1).replace(',', '.'))

# Extraction du take profit 1
donnees['Take profit 1'] = float(re.search(r'Take profit 1 : ([\d,]+)', texte).group(1).replace(',', '.'))

# Extraction du take profit 2
donnees['Take profit 2'] = float(re.search(r'Take profit 2 : ([\d,]+)', texte).group(1).replace(',', '.'))

# Création de la chaîne multiligne
resultat = f"""Paire : {donnees['Paire']}
Prix d'achat : {donnees['Prix achat']}
Stop loss : {donnees['Stop loss']}
Take profit 1 : {donnees['Take profit 1']}
Take profit 2 : {donnees['Take profit 2']}"""

# Affichage du résultat
print(resultat)
