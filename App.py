import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="365 Gym & Fitness", page_icon="🏋️", layout="wide")

# 2. EN-TÊTE : LOGO ET TITRE
col_logo, col_titre = st.columns([1, 4])
with col_logo:
    # On utilise un bloc "try" pour éviter que l'app plante si l'image manque
    try:
        st.image("logo_365.jpg", width=150)
    except:
        st.warning("Logo non trouvé")

with col_titre:
    st.title("365 GYM & FITNESS")
    st.subheader("Tableau de Bord de Gestion")

st.divider()

# 3. DONNÉES TEMPORAIRES (Pour que ça marche tout de suite)
data = {
    'Nom': ['Jean Dupont', 'Marie Martin', 'Isaac Kabuya', 'Sarah Luvumbu'],
    'Téléphone': ['+24381000000', '+24399000000', '+24382000000', '+24385000000'],
    'Date_Fin': ['2026-03-28', '2026-04-15', '2026-03-28', '2026-05-01'],
    'Type': ['Mensuel', 'Trimestriel', 'Mensuel', 'Annuel']
}
df = pd.DataFrame(data)
df['Date_Fin'] = pd.to_datetime(df['Date_Fin'])

# 4. STATISTIQUES (RAPPORTS)
st.subheader("📊 Rapport d'activité")
col1, col2, col3 = st.columns(3)
col1.metric("Total Abonnés", len(df))
col2.metric("Abonnements Actifs", len(df))
# On calcule ceux qui expirent dans 3 jours (par rapport à aujourd'hui)
expire_3j = len(df[df['Date_Fin'].dt.date == (datetime.now() + timedelta(days=3)).date()])
col3.metric("Expirations (3j)", expire_3j)

# 5. RECHERCHE ET FILTRES
st.subheader("🔍 Recherche d'Abonnés")
c1, c2 = st.columns(2)
nom_cherche = c1.text_input("Rechercher par nom")
mois_selectionne = c2.selectbox("Filtrer par mois d'échéance", 
    ["Tous", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"])

# Application des filtres
df_filtre = df.copy()
if nom_cherche:
    df_filtre = df_filtre[df_filtre['Nom'].str.contains(nom_cherche, case=False)]

# Affichage du tableau final
st.dataframe(df_filtre, use_container_width=True)

# 6. BOUTON DE TÉLÉCHARGEMENT
st.download_button("📥 Télécharger le rapport complet", df_filtre.to_csv(index=False), "rapport_365gym.csv")
