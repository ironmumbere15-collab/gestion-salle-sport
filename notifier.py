import sqlite3
from datetime import datetime, timedelta

# Connexion à la base
conn = sqlite3.connect('membres.db')
cursor = conn.cursor()

# On cherche les abonnements qui expirent dans les 5 prochains jours
seuil = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')

cursor.execute("SELECT nom, email, date_fin FROM abonnes WHERE date_fin <= ?", (seuil,))
expirations = cursor.fetchall()

if expirations:
    print(f"Alerte : {len(expirations)} abonnements se terminent bientôt !")
    for nom, email, date in expirations:
        print(f"Notifier {nom} ({email}) - Fin le {date}")
        # Ici on ajoutera plus tard l'envoi d'email réel
else:
    print("Tout est à jour, aucune notification à envoyer.")

conn.close()
