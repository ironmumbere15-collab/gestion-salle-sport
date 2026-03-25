import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Logo en haut de la barre latérale ---
st.sidebar.image("https://via.placeholder.com/200x80.png?text=Logo+Salle+de+Sport", width=200)

# --- Menu latéral ---
section = st.sidebar.radio(
    "Navigation",
    ["Tableau de Bord", "Abonnés", "Abonnés Expirés", "Ajouter Abonné", "Forum", "Contact", "Photos/Vidéos"]
)

# --- Données simulées abonnés ---
data = {
    'Nom': ['Jean Dupont', 'Marie Martin', 'Isaac Kabuya', 'Sarah Luvumbu'],
    'Téléphone': ['+24381000000', '+24399000000', '+24382000000', '+24385000000'],
    'Date_Fin': ['2024-05-28', '2024-06-15', '2024-05-28', '2024-07-01'],
    'Type': ['Mensuel', 'Trimestriel', 'Mensuel', 'Annuel']
}
df = pd.DataFrame(data)
df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])

# --- Dates importantes ---
aujourdhui = datetime.now().date()
dans_3_jours = aujourdhui + timedelta(days=3)

# --- Sections ---
if section == "Tableau de Bord":
    st.title("🏋️ Tableau de Bord de la Salle de Sport")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Abonnés", len(df))
    col2.metric("Abonnements Actifs", len(df[df['Date_Fin'].dt.date >= aujourdhui]))
    col3.metric("Expirations (3j)", len(df[df['Date_Fin'].dt.date == dans_3_jours]))

elif section == "Abonnés":
    st.subheader("⚠️ Abonnés expirant dans 3 jours")
    expirant_bientot = df[df['Date_Fin'].dt.date == dans_3_jours]
    if not expirant_bientot.empty:
        st.dataframe(expirant_bientot)
        if st.button("📣 Notifier les abonnés expirant bientôt"):
            for idx, user in expirant_bientot.iterrows():
                message = f"Bonjour {user['Nom']}, votre abonnement se termine le {user['Date_Fin'].date()}. Merci de le renouveler !"
                st.success(f"Notification prête pour {user['Nom']} ({user['Téléphone']}): {message}")
    else:
        st.info("Aucun abonné n'expire dans 3 jours.")

elif section == "Abonnés Expirés":
    st.subheader("⛔ Abonnés expirés")
    expirés = df[df['Date_Fin'].dt.date < aujourdhui]
    if not expirés.empty:
        st.dataframe(expirés)
    else:
        st.info("Aucun abonné expiré pour le moment.")

elif section == "Ajouter Abonné":
    st.subheader("➕ Ajouter un nouvel abonnement")
    with st.form("form_nouvel_abonne"):
        nom = st.text_input("Nom complet")
        telephone = st.text_input("Téléphone")
        date_fin = st.date_input("Date de fin d'abonnement")
        type_abonnement = st.selectbox("Type d'abonnement", ["Mensuel", "Trimestriel", "Annuel"])
        
        st.write("Actions :")
        c1, c2, c3 = st.columns(3)
        ajouter = c1.form_submit_button("Ajouter")
        modifier = c2.form_submit_button("Modifier")
        supprimer = c3.form_submit_button("Supprimer")
        if ajouter:
            st.success(f"Abonné {nom} ajouté !")
        if modifier:
            st.warning(f"Abonné {nom} modifié !")
        if supprimer:
            st.error(f"Abonné {nom} supprimé !")

elif section == "Forum":
    st.subheader("💬 Forum de discussion")
    st.info("Ici tu pourras poster et lire les messages des abonnés (fonctionnalité à connecter).")

elif section == "Contact":
    st.subheader("📱 Contact WhatsApp")
    st.info("Lien direct vers ton numéro WhatsApp : [Clique ici](https://wa.me/24381000000)")

elif section == "Photos/Vidéos":
    st.subheader("📸 Galerie")
    st.info("Ici tu pourras poster tes photos et vidéos de la salle de sport.")
